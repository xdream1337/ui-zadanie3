import random
from operator import attrgetter

# CONFIG VALUES
N_POPULATION = 10
N_GENERATIONS = 10
MUTATION_PERCENTAGE = 3
DEBUG = 1

class Seeker():
    def __init__(self): 
        self.moves = []
        self.genome = []
        self.fitness = 0
        self.treasures = 0
    
    def __eq__(self, other): 
        if not isinstance(other, Seeker):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.moves == other.moves and self.genome == other.genome and self.fitness == other.fitness and self.treasures == other.treasures

def read_gamefile():
    game_file = open('gamefile.txt', 'r')
    treasure_pos = []
    
    for i, line in enumerate(game_file):
        # nacital som prazdny riadok, break z loopu
        if not line:
            break
        
        line = line.strip().split(' ') 
        x = int(line[0])
        y = int(line[1])
        # nacitavam velkost x, y mapy
        if (i == 0):
            game_size = (x, y)
        # nacitavam poziciu hladaca pokladu
        elif (i == 1):
            seeker_start_pos = (x, y)
        # nacitavam pozicie pokladov
        elif (i > 1):
            treasure_pos.append([x, y])
    
    return game_size, seeker_start_pos, treasure_pos

game_size, seeker_start_pos, treasure_pos = read_gamefile()
print(len(treasure_pos))

def calculate_move(gene):
    move = gene & 3
    
    if move == 0:
        return 'H'
    elif move == 1:
        return 'D'
    elif move == 2:
        return 'L'
    elif move == 3:
        return 'R'

def calculate_treasures(seeker, pos):
    for treasure in treasure_pos:
        if treasure[0] == pos[0] and treasure[1] == pos[1]:
            seeker.fitness += 1
            seeker.treasures += 1
            treasure_pos.remove(treasure)

def calculate_fitness(seeker):
    number_of_moves = len(seeker.moves)
    seeker_pos = [seeker_start_pos[0], seeker_start_pos[1]]
    
    for i in range(0, number_of_moves):
        move = seeker.moves[i]
        
        if move == 'H':
            seeker_pos[0] -= 1
            if seeker_pos[0] < 0:
                break
        elif move == 'D':
            seeker_pos[0] += 1
            if seeker_pos[0] > game_size[0]:
                break
        elif move == 'L':
            seeker_pos[1] -= 1
            if seeker_pos[1] < 0:
                break
        elif move == 'R':
            seeker_pos[1] += 1
            if seeker_pos[1] > game_size[1]:
                break
        
        calculate_treasures(seeker, seeker_pos)
    
    seeker.fitness -= len(seeker.moves)/1000
        

def virtual_machine(seeker):
    instruction_counter = 0
    
    # pocet genov ma byt vzdy 64
    for i in range(0, 64):
        
        if instruction_counter > 500:
            break
        else:
            instruction_counter += 1
        
        instruction = seeker.genome[i] >> 6
        address = seeker.genome[i] & 63
        
        # inkrementacia
        if instruction == 0:
            seeker.genome[address] += 1
        elif instruction == 1:
            seeker.genome[address] -= 1
        elif instruction == 2:
            i = address
        elif instruction == 3:
            seeker.moves.append(calculate_move(seeker.genome[address])) # spytat sa ci i alebo address 
        
            
def create_genome(seeker):
    seeker.genome = [int(random.randint(0, 255)) for i in range(64)]

def generate_first_population(n_population):
    generation = []
    
    for i in range(0, n_population):
        seeker = Seeker()
        create_genome(seeker)
        generation.append(seeker)
        
    return generation

"""
def tournament(generation, k):
    best_player = None
    
    for i in range(0, k):
        player = generation[random.randint(0, N_POPULATION-1)]
        if best_player is None or player.fitness > best_player.fitness:
            best_player = player
    
    return best_player"""
    
def tournament(generation, k):
    contestants = []
    for i in range(k):
       contestants.append(random.choice(generation))
    return max(contestants, key=attrgetter('fitness'))

def tournament_start(generation, k):
    seeker_1 = None
    seeker_2 = None
    
    while True:
        seeker_1 = tournament(generation, k)
        seeker_2 = tournament(generation, k)
        
        #print('seeker1', seeker_1.moves, seeker_1.genome, seeker_1.fitness, seeker_1.treasures)
        #print('seeker1', seeker_2.moves, seeker_2.genome, seeker_2.fitness, seeker_2.treasures)
        
        #print(seeker_1 != seeker_2)
        if not seeker_1 is seeker_2:
            break
        
    #print('TOURNAMENT RETURN')
    #print('seeker1', seeker_1.moves, seeker_1.genome, seeker_1.treasures, seeker_1.fitness)
    #print('seeker1', seeker_2.moves, seeker_2.genome, seeker_2.treasures, seeker_2.fitness)
        
    return [seeker_1, seeker_2]

def crossover(seekers):     
    #funkcia na krizenie jedincov
    crossover_point = random.randint(0, 63)
    
    seeker_1 = Seeker()
    seeker_2 = Seeker()
    
    for i in range(0, 64):
        if i >= crossover_point:
            seeker_1.genome.append(seekers[1].genome[i])
            seeker_2.genome.append(seekers[0].genome[i])
        else:
            seeker_1.genome.append(seekers[0].genome[i])
            seeker_2.genome.append(seekers[1].genome[i])
            
            
    #print('seeker1 treasures', seeker_1.treasures, ' moves', seeker_1.moves, '  genome', seeker_1.genome, 'treasures', seeker_1.treasures, 'fitness', seeker_1.fitness)
    #print('seeker2 treasures', seeker_2.treasures, ' moves', seeker_2.moves, '  genome', seeker_2.genome, 'treasures', seeker_2.treasures, 'fitness', seeker_2.fitness)
    
    return [seeker_1, seeker_2]

def mutate(seeker):
    for i in range(0, 64):
        mutate_percentage = random.randint(0, 100)
        if mutate_percentage < MUTATION_PERCENTAGE:
            seeker.genome[i] = random.randint(0, 255)
            
print("Game size:", game_size)
print("Seeker start pos:", seeker_start_pos)
print("Treasure positions:", treasure_pos)

generation = generate_first_population(N_POPULATION)
    
def game_start(generation):
    game_size, seeker_start_pos, treasure_pos = read_gamefile()
    for i in range(N_GENERATIONS):
        print('Generacia cislo', i, "z", str(N_GENERATIONS))
        max_treasures = 0
        
        for seeker in generation:
            virtual_machine(seeker)
            calculate_fitness(seeker)
            
            if seeker.treasures > max_treasures:
                max_treasures = seeker.treasures

            print('seeker treasures', seeker.treasures, ' moves', seeker.moves, '  genome', seeker.genome, 'treasures', seeker.treasures)
                        
            if seeker.treasures == len(treasure_pos):
                print('hej hou, hej hou, nasiel som vsetky poklady!!!!', max_treasures)
                return
            
                
            
        new_generation = []

        for i in range(int(len(generation)/2)):
            seekers = tournament_start(generation, 3)
            #seekers = [x,y]
            new_seekers = crossover(seekers)
            mutate(new_seekers[0])
            mutate(new_seekers[1])
            #virtual_machine(new_seekers[0])
            #irtual_machine(new_seekers[1])
            #print('crossover seeker1 moves', new_seekers[0].moves, new_seekers[0].genome, new_seekers[0].treasures, new_seekers[0].fitness)
            #print('crossover seeker2 moves', new_seekers[1].moves, new_seekers[1].genome, new_seekers[1].treasures, new_seekers[1].fitness)
            new_generation.append(new_seekers[0])
            new_generation.append(new_seekers[1])
        
        generation.clear()
        generation.extend(new_generation)
        


game_start(generation)




        
        

    
    
            