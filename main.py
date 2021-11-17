import random
from operator import attrgetter

# CONFIG VALUES
N_POPULATION = 20
N_GENERATIONS = 10
MUTATION_PERCENTAGE = 3
DEBUG = 1

class Seeker():
    def __init__(self,genome, moves, fitness, treasures): 
        self.moves = moves
        self.genome = genome
        self.fitness = fitness
        self.treasures = treasures
    
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
    counter = 0
    while gene != 0:
        if gene & 1:
            counter += 1

        gene = gene >> 1

    if 0 <= counter <= 2:
        return 'H'
    elif 2 < counter <= 4:
        return 'D'
    elif 4 < counter <= 6:
        return 'P'
    elif 6 < counter <= 8:
        return 'L'

def calculate_treasures(seeker, pos, size, treasures):
    if pos[0] < size[0] and pos[1] < size[1]:                                 #a ich nasledne odstranenie, aby sa program
        for each in treasures:                                              #necyklil
            if pos[0] == each[0] and pos[1] == each[1]:
                seeker.treasures += 1
                treasures.remove(each)
        return True
    return False

def how_many_treasures(seeker, seeker_start_pos, game_size, treasures):
    number_of_moves = len(seeker.moves)
    seeker_pos = [seeker_start_pos[0], seeker_start_pos[1]]
    
    for i in range(0, number_of_moves):
        move = seeker.moves[i]
        
        if move == 'H':
            seeker_pos[1] -= 1
            if not calculate_treasures(seeker, seeker_pos, game_size, treasures):
                break
        elif move == 'D':
            seeker_pos[1] += 1
            if not calculate_treasures(seeker, seeker_pos, game_size, treasures):
                break
        elif move == 'L':
            seeker_pos[0] -= 1
            if not calculate_treasures(seeker, seeker_pos, game_size, treasures):
                break
        elif move == 'R':
            seeker_pos[0] += 1
            if not calculate_treasures(seeker, seeker_pos, game_size, treasures):
                break

def get_fitness(seeker):
    fitness = 0
    if seeker.treasures != 0:
        fitness = 1000 * int(seeker.treasures) - len(seeker.moves)
    else:
        fitness -= len(seeker.moves)
    
    return fitness
        

def virtual_machine(genome):
    tapeindex = 0
    moves = []
    
    # pocet genov ma byt vzdy 64
    for i in range(500):
        
        instruction = genome[tapeindex] >> 6
        address = genome[tapeindex] & 63
        
        # inkrementacia
        if instruction == 0:
            genome[address] += 1
        elif instruction == 1:
            genome[address] -= 1
        elif instruction == 2:
            tapeindex = address
        elif instruction == 3:
            moves.append(calculate_move(genome[tapeindex])) # spytat sa ci i alebo address 
        
        if instruction != 2:
            tapeindex += 1
            if tapeindex > 63:
                tapeindex = 0
                
    
    return moves
        
            
def create_genome():
    return [int(random.randint(0, 255)) for i in range(64)]

def generate_first_population(n_population):
    generation = []
    
    for i in range(0, n_population):
        genome = create_genome()
        seeker = Seeker(genome, virtual_machine(genome), 0, 0) 
        
        print(seeker.genome, seeker.moves)
        
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
        
    return seeker_1, seeker_2

def crossover(seekers):     
    #funkcia na krizenie jedincov
    crossover_point = random.randint(0, len(seekers[0].genome)-1)
    
    genome_1, genome_2 = [], []
    
    for i in range(0, 64):
        if i >= crossover_point:
            genome_1.append(seekers[1].genome[i])
            genome_2.append(seekers[0].genome[i])
        else:
            genome_1.append(seekers[0].genome[i])
            genome_2.append(seekers[1].genome[i])
    
    seeker_1 = Seeker(genome_1, virtual_machine(genome_1), 0, 0)
    seeker_2 = Seeker(genome_2, virtual_machine(genome_2), 0, 0) 
            
            
    #print('seeker1 treasures', seeker_1.treasures, ' moves', seeker_1.moves, '  genome', seeker_1.genome, 'treasures', seeker_1.treasures, 'fitness', seeker_1.fitness)
    #print('seeker2 treasures', seeker_2.treasures, ' moves', seeker_2.moves, '  genome', seeker_2.genome, 'treasures', seeker_2.treasures, 'fitness', seeker_2.fitness)
    
    return seeker_1, seeker_2

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
            how_many_treasures(seeker, seeker_start_pos, game_size, treasure_pos)
            
            if seeker.treasures > max_treasures:
                max_treasures = seeker.treasures

            
                        
            if seeker.treasures == 2:
                print('hej hou, hej hou, nasiel som vsetky poklady!!!!', max_treasures)
                return
            else:
                seeker.fitness = get_fitness(seeker)
            
            print('seeker treasures', seeker.treasures, ' moves', seeker.moves, '  genome', seeker.genome, 'treasures', seeker.treasures, seeker.fitness)
            
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










        
        

    
    
            