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
    def __init__(self, id, size=100, habitability=100, name=""):
        self.id = id
        self.name = name
        self.size = size                    # Planet size. One unit is 100 million on people
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
        self.orglevel = orglevel
        self.orglevel_progress = 0.0
        self.stability = stability

    def __str__(self):
        text = (f'Planet ID:\t{self.planet_id}\n'
            f'Name:\t{self.name}\n'
            f'Population:\t{self.population}\n'     # In thousands of people
            f'Techlevel:\t{self.techlevel}\n'       # Techlevel. From 1 to 20
            f'Orglevel:\t{self.orglevel}\n'         # Orglevel. From 1 to 20
            f'Stability:\t{self.stability}')        # Internal stability of society (very basic approach).
        return text

    def calculate_stability(self, turn):
        # Calculate random events each 10 turns
        if (turn % 10 == 0):
            r = int(random.gauss(0.5, 10 / self.orglevel) * 1000 + 4500)
            if r > 1 and r < 1000:
                # Epic failure event
                stab_change = int(self.stability * -0.85)

            else:
                stab_change = int((r - 5000) * 0.002 * self.techlevel)


            self.stability += stab_change

        if self.stability > 10000: self.stability = 10000
        if self.stability < 1: self.stability = 1

    def calculate_orglevel(self, turn, planet_habitability):

        if turn % 10 == 0:
            org_change = (random.random() - 0.5) * ((99 / (self.population / 1000000)) + 1)
        else:
            org_change = (self.stability ** (0.25) - 8) * (10 / planet_habitability)

        self.orglevel_progress += org_change

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
max_turns = 1000001

# Lists for plotting graps
plot_turn = []
plot_orglevel = []
plot_stability = []
#plot_r = []

colonies = []
temp_colony = Colony(terra_id, 1000000, 10, 10, 7000, "Terra")
# print(temp_colony)


# print(settings, '\n\n\n')
# print(stars[0].planets[0], '\n\n')
# print(stars[0])

for turn in range(1, max_turns):
    # print(turn)
    plot_turn.append(turn)
    plot_stability.append(temp_colony.stability)
    plot_orglevel.append(temp_colony.orglevel * 500)

    temp_colony.calculate_stability(turn)
    temp_colony.calculate_orglevel(turn, 100)

plt.plot(plot_turn, plot_stability)
plt.plot(plot_turn, plot_orglevel)
#plt.plot(plot_turn, plot_r)
print("*****")
print(f"min(stability)={min(plot_stability)}")
print(f"max(stability)={max(plot_stability)}")
# print(f"min(random)={min(plot_r)}")
# print(f"max(random)={max(plot_r)}")

# for i in range(1,20):
#     print(i, (i**2 * 10),int(-1* ((20-i)**1.6 * 10 + 300)))

plt.show()


