import random
import math
import matplotlib.pyplot as plt

def calc_range(x1, y1, x2, y2):
    """
    Calculate range between two point on map
    """
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class Star():
    def __init__(self, id, x=0, y=0, name=""):
        self.id = id
        self.type = 0   # Defined for later use
        self.name = name
        self.x = x      # Global coordinates
        self.y = y
        self.inclination = 0        # Orbital plane inclination from default plane
        self.asc_node_angle = 0     # Longtitude of ascending node
        self.planets = []           # List of planets

    def __str__(self):
        text = (f'ID:\t{self.id}\n'
            f'Name:\t{self.name}\n'
            f'X:\t{self.x}\n'
            f'Y:\t{self.y}\n'
            f'Type:\t{self.type}\n'
            f'Inclination:\t{self.inclination}\n'
            f'Ascending node:\t{self.asc_node_angle}')
        return text

class Planet():
    def __init__(self, id, size=1000, habitability=100, name=""):
        self.id = id
        self.name = name
        self.size = size                    # Planet size. One unit for 1 million on people
        self.habitability = habitability    # from 0 to 125. 100 is default "Earth" habitability

    def __str__(self):
        text = (f'ID:\t{self.id}\n'
            f'Name:\t{self.name}\n'
            f'Size:\t{self.size}\n'
            f'Habitability:\t{self.habitability}\n')
        return text

class Colony():
    def __init__(self, planet_id, population, techlevel, orglevel, stability, name=""):
        self.planet_id = planet_id
        self.name = name
        self.population = population
        self.techlevel = techlevel
        self.techlevel_progress = 0.0
        self.orglevel = orglevel
        self.orglevel_progress = 0.0
        self.stability = stability

        self.is_dead = False

    def __str__(self):
        text = (f'Planet ID:\t{self.planet_id}\n'
            f'Name:\t{self.name}\n'
            f'Population:\t{self.population}\n'     # In thousands of people
            f'Techlevel:\t{self.techlevel}\n'       # Techlevel. From 1 to 20
            f'Orglevel:\t{self.orglevel}\n'         # Orglevel. From 1 to 20
            f'Stability:\t{self.stability}')        # Internal stability of society (very basic approach).
        return text

    def check_colony(self, turn):
        if self.population < 1:
            self.is_dead = True
            print(f"DEAD turn {turn}")

    def calculate_population(self, turn, planet_habitability, planet_size):
        global apocalipse_counter
        global global_coefficent

        # Definitions: survivability depends on minimal techlevel
        techlevel_surv = {
            0: 95,
            1: 95,
            2: 93,
            3: 91,
            4: 89,
            5: 85,
            6: 80,
            7: 75,
            8: 70,
            9: 65,
            10: 60,
            11: 55,
            12: 50,
            13: 45,
            14: 40,
            15: 35,
            16: 30,
            17: 25,
            18: 18,
            19: 10,
            20: 0
        }

        # Check for deadly conditions
        if planet_habitability < techlevel_surv[self.techlevel]:
            self.population = 0
            self.is_dead = True


        # Calculate relative survivability
        rel_habitability = planet_habitability - techlevel_surv[self.techlevel]
        if self.stability != 5500:
            rel_stability = float((self.stability - 5500) / 1000)
            # print(self.stability, rel_stability)
        else:
            rel_stability = 0.001

        # Check for overpopulation
        if (self.population / init_max_pop) < 0.5:
            pop_limiter = 1 - (self.population / init_max_pop)
        else:
            pop_limiter = (1 - (self.population / init_max_pop)) * 0.1

        # Main pop change calculation
        pop_change = 0.00001 * rel_habitability * rel_stability * pop_limiter * global_coefficent

        if (turn % 10 == 0):
            pass
            # print(pop_change)
        

        self.population = int(self.population + (self.population * pop_change))


        # Limit population to planet size * planet habitability
        self.population = min([self.population, planet_size * planet_habitability / 100])

    def calculate_stability(self, turn):
        global apocalipse_counter
        global global_coefficent

        r = int(random.gauss(0.5, 10 / self.orglevel) * 1000 + 4500)

        # Epic failure is possible event every 10 turns
        if (turn % 10 == 0):
            if r > 1 and r < 1000:
                # Epic failure event
                stab_change = int(self.stability * -0.85)
                
        if apocalipse_counter < 1000:
            stab_change = int((r - 5000) * 0.002 * self.techlevel)
        else:
            stab_change = int((r - 4500) * 0.002 * self.techlevel)

        self.stability += (stab_change * global_coefficent)

        # Limiters for stability parameter
        if self.stability > 10000: self.stability = 10000
        if self.stability < 1: self.stability = 1

        # Calculate apocalypce counter: time for bad conditions.
        # After counter fills up, crutch will be used to make things better
        if self.stability < 2500:
            apocalipse_counter += 1
        else:
            apocalipse_counter -= 1
            if apocalipse_counter < 0: apocalipse_counter = 0

    def calculate_orglevel(self, turn, planet_habitability):
        global global_coefficent
        if turn % 10 == 0:
            org_change = (random.random() - 0.5) * min([(50 / (self.population / 1000000)), 1])
        else:
            org_change = (self.stability ** (0.25) - 8) * (10 / planet_habitability)

        self.orglevel_progress += (org_change * global_coefficent)

        # Levelup code
        if self.orglevel_progress > (self.orglevel**2 * 10):
            self.orglevel += 1
            self.orglevel_progress = 0

        # Leveldown code
        elif self.orglevel_progress < (-1 * ((20 - self.orglevel)**1.6 * 10 + 300)):
            self.orglevel -= 1
            self.orglevel_progress = 0

        # Verifing ranges
        if self.orglevel > 20: self.orglevel = 20
        if self.orglevel < 1: self.orglevel = 1

    def calculate_techlevel(self, turn, planet_habitability):
        global global_coefficent

        pop_coeff = (self.population / 1000000)
        if pop_coeff > 10: pop_coeff = 10

        if turn % 10 == 0:
            tech_change = (random.random() - 0.5) * max([(self.population / 1000000), 50])
        else:
            tech_change = (self.population ** (0.4) - 100) * (10 / planet_habitability)

        self.techlevel_progress += (tech_change * global_coefficent)


        # Levelup code
        if self.techlevel_progress > (self.techlevel**2 * 10):
            self.techlevel += 1
            self.techlevel_progress = 0

        # Leveldown code
        elif self.techlevel_progress < (-1 * ((20 - self.orglevel)**1.6 * 10 + 300)):
            self.techlevel -= 1
            self.techlevel_progress = 0

        # Verifing ranges
        if self.techlevel > 20: self.techlevel = 20
        if self.techlevel < 1: self.techlevel = 1       

# Settings
class Settings():
    def __init__(self):
        self.max_stars = 1000           # Maximum number of star systems in simulation
        self.field_size_x = 31546       # Width of simulation field in light megaseconds
        self.field_size_y = 31546       # Height of simulation field in light megaseconds
        self.min_star_distance = 10     # Minimum range between two star systems
        self.max_planets = 1            # Max planet per star
        self.planet_min_size = 1
        self.planet_max_size = 150
        self.planet_min_habitability = 1
        self.planet_max_habitability = 125

        # You can turn off calculation of some parameters entirely if needed
        self.calculate_population = True
        self.calculate_techlevel = True
        self.calculate_orglevel = True
        self.calculate_stability = True


    def __str__(self):
        text = (f'Max stars in simulation:\t{self.max_stars}\n'
            f'Field width:\t{self.field_size_x}\n'
            f'Field height:\t{self.field_size_y}\n'
            f'Min distance between stars:\t{self.min_star_distance}\n'
            f'Max planets per star:\t{self.max_planets}\n'
            f'Min planet size:\t{self.planet_min_size}\n'
            f'Max planet size:\t{self.planet_max_size}\n'
            f'Min planet habitability:\t{self.planet_min_habitability}\n'
            f'Max planet habitability:\t{self.planet_max_habitability}\n')
        return text


def initial_system_generation():
    """
    Generating stars and planets without colonies
    """
    # Generating stars
    stars = []
    id_counter = 1

    # Generate first star
    temp_star = Star(id=id_counter, x=(settings.field_size_x // 2), y=(settings.field_size_y // 2), name="Sol")
    id_counter += 1

    temp_planet = Planet(id_counter, size=100, habitability=100, name="Terra")
    temp_star.planets.append(temp_planet)
    terra_id = id_counter
    id_counter += 1
    stars.append(temp_star)

    while len(stars) <= settings.max_stars:
        flag_generated = False
        x = 0
        y = 0

        # Generating star
        while not flag_generated:   # Repeat generation process until it succeeds
            x = random.randrange(settings.field_size_x)
            y = random.randrange(settings.field_size_y)
            flag_generated = True
            for star in stars:
                rng = calc_range(x, y, star.x, star.y)
                if rng < settings.min_star_distance:
                    flag_generated = False
                    break
        temp_star = Star(id_counter, x, y)
        id_counter += 1

        # Generating planet
        temp_planet = Planet(id=id_counter,
            size=random.randrange(settings.planet_min_size, settings.planet_max_size),
            habitability=random.randrange(settings.planet_min_habitability, settings.planet_max_habitability))
        id_counter += 1
        temp_star.planets.append(temp_planet)
        stars.append(temp_star)

    return stars, terra_id

# Init
settings = Settings()
stars, terra_id = initial_system_generation()
apocalipse_counter = 0


# Starting parameters for simulation
init_pop = 10000000
init_max_pop = 100000000
init_techlevel = 10
init_orglevel = 10
init_stability = 7000
init_max_turns = 100001
init_habitability = 100
global_coefficent = 10      # Every parameter's calculation (increase/decrease) is multiplied by this number; Higher values will speed simulation


# Empty lists for graphs plotting
plot_turn = []
plot_orglevel = []
plot_techlevel = []
plot_stability = []
plot_population = []

colonies = []
temp_colony = Colony(terra_id, init_pop, init_techlevel, init_orglevel, init_stability, "Terra")
# print(temp_colony)


# print(settings, '\n\n\n')
# print(stars[0].planets[0], '\n\n')
# print(stars[0])

for turn in range(1, init_max_turns):
    plot_turn.append(turn)
    plot_stability.append(temp_colony.stability)
    plot_orglevel.append(temp_colony.orglevel * 500)
    plot_techlevel.append(temp_colony.techlevel * 500)
    plot_population.append(temp_colony.population)

    temp_colony.check_colony(turn)
    if not temp_colony.is_dead:
        if settings.calculate_stability: temp_colony.calculate_stability(turn)
        if settings.calculate_orglevel: temp_colony.calculate_orglevel(turn, init_habitability)
        if settings.calculate_techlevel: temp_colony.calculate_techlevel(turn, init_habitability)
        if settings.calculate_population: temp_colony.calculate_population(turn, init_habitability, init_max_pop)
    else:
        break

# Printing simulation results
print("*****")
print(f"min(Population)={min(plot_population)}")
print(f"max(Population)={max(plot_population)}")
print(f"min(TechLevel)={min(plot_techlevel)}")
print(f"max(TechLevel)={max(plot_techlevel)}")
print(f"min(OrgLevel)={min(plot_orglevel)}")
print(f"max(OrgLevel)={max(plot_orglevel)}")
print(f"min(stability)={min(plot_stability)}")
print(f"max(stability)={max(plot_stability)}")

# Drawing graphs
fig, ax1 = plt.subplots(figsize=(14, 8))

ax2 = ax1.twinx()
ax1.plot(plot_turn, plot_stability, color='b')
ax1.plot(plot_turn, plot_techlevel, color='y')
ax1.plot(plot_turn, plot_orglevel, color='g')
ax2.plot(plot_turn, plot_population, color='r')

ax1.set_xlabel('Turns')
ax1.set_ylabel('Stability')
ax2.set_ylabel('Population')

plt.show()
