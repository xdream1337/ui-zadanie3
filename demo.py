import random
from copy import deepcopy

class Seeker():
    def __init__(self, genome, moves, fitness, treasures): 
        self.moves = moves
        self.genome = genome
        self.fitness = fitness
        self.treasures = treasures
    
    def __eq__(self, other): 
        if not isinstance(other, Seeker):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.moves == other.moves and self.genome == other.genome and self.fitness == other.fitness and self.treasures == other.treasures


def mutate(child):                                                          #funkcia pre mutaciu jedincov
    for i in range(64):
        random_num = random.randint(1, 100)
        if random_num <= 3:
            child.genome[i] = random.randint(0, 255)


def crossover(seeker_1, seeker_2):                                    #funkcia na krizenie jedincov
    crossover_point = random.randint(0, 63)
    
    genome_1 = []
    genome_2 = []
    
    for i in range(64):
        if i >= crossover_point:
            genome_1.append(seeker_2.genome[i])
            genome_2.append(seeker_1.genome[i])
        else:
            genome_1.append(seeker_1.genome[i])
            genome_2.append(seeker_2.genome[i])
            
    seeker_parent_1 = Seeker(genome_1, virtual_machine(genome_1[:]), 0, 0)
    seeker_parent_2 = Seeker(genome_2, virtual_machine(genome_2[:]), 0, 0)
    
    return seeker_parent_1, seeker_parent_2



def tournament(generation, k):
    best_player = None
    
    for i in range(k):
        player = random.choice(generation)
        if best_player is None or player.fitness > best_player.fitness:
            best_player = player
    
    return best_player

def tournament_start(generation, k):
    while True:
        seeker_1 = tournament(generation, k)
        seeker_2 = tournament(generation, k)
        
        #print('seeker1', seeker_1.moves, seeker_1.genome, seeker_1.fitness, seeker_1.treasures)
        #print('seeker1', seeker_2.moves, seeker_2.genome, seeker_2.fitness, seeker_2.treasures)
        
        #print(seeker_1 != seeker_2)
        if seeker_1 != seeker_2:
            break
        
    #print('TOURNAMENT RETURN')
    #print('seeker1', seeker_1.moves, seeker_1.genome, seeker_1.treasures, seeker_1.fitness)
    #print('seeker1', seeker_2.moves, seeker_2.genome, seeker_2.treasures, seeker_2.fitness)
        
    return seeker_1, seeker_2

def elitism(generation, count):
    elites = []
    
    gen_deepcopy = deepcopy(generation)
    gen_deepcopy.sort(key=lambda x: x.fitness, reverse=True)
    
    for i in range(count):
        elites.append(gen_deepcopy[i])
    
    return elites


def count_treasures(seeker, pos, treasures):   
    treasures_deepcopy = deepcopy(treasures)   
    
    for treasure in treasures_deepcopy:
        if pos[0] == treasure[0] and pos[1] == treasure[1]:
            seeker.treasures += 1
            treasures_deepcopy.remove(treasure)
    
    if len(treasures_deepcopy) == 0:
        return True


def check_solution_and_fitness(start_pos, treasures, seeker, size): 
    solution = []#funkcia simulujuca pohyb po mape
    pos = [start_pos[0], start_pos[1]]
    fitness = 0
    
    for move in seeker.moves:
        if move == 'U':
            pos[1] -= 1
            if pos[1] < 0 or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'D':
            pos[1] += 1
            if pos[1] > size[1] or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'L':
            pos[0] -= 1
            if pos[0] < 0 or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'R':
            pos[0] += 1
            if pos[0] > size[0] or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
                
    if seeker.treasures > 0:
        fitness = seeker.treasures - (len(solution)/1000)
    else:
        fitness -= (len(solution)/1000)
        
    return solution, fitness


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
            game_size = [x, y]
        # nacitavam poziciu hladaca pokladu
        elif (i == 1):
            seeker_start_pos = [x, y]
        # nacitavam pozicie pokladov
        elif (i > 1):
            treasure_pos.append([x, y])
    
    return game_size, seeker_start_pos, treasure_pos, len(treasure_pos)

def calculate_move(gene):                             
    move = gene & 3
    
    if move == 0:
        return 'U'
    elif move == 1:
        return 'D'
    elif move == 2:
        return 'L'
    elif move == 3:
        return 'R'


def virtual_machine(genome):   
    #funkcia pomocou ktorej ziskame cestu kazdeho jedinca
    index = 0
    moves = []
    
    for i in range(500):
        instruction = genome[index] >> 6
        address = genome[index] & 63

        if instruction == 0:
            genome[address] += 1
        elif instruction == 1:
            genome[address] -= 1
        elif instruction == 2:
            index = address
        elif instruction == 3:
            moves.append(calculate_move(genome[index]))

        if instruction != 2:
            index += 1
            if index > 63:
                index = 0
    
    return moves


def create_genome():   
    return [int(random.randint(0, 255)) for i in range(64)] 


    
def generate_first_population(n_population):
    generation = []
    
    for i in range(0, n_population):
        genome = create_genome()
        seeker = Seeker(genome, virtual_machine(genome[:]), 0, 0) 
        
        print(seeker.genome, seeker.moves)
        
        generation.append(seeker)
        
    return generation

N_GENERATIONS = int(input('Zadajte pocet generacii: '))
N_POPULATION = int(input('Zadajte pocet jedincov pre jednu populaciu: '))
ELITISM_COUNT = 2

def life_cycle():     
    game_size, start_pos, treasures, treasure_count = read_gamefile()
    generation = generate_first_population(N_POPULATION)
    
    for i in range(int(N_GENERATIONS)):
        print('Generacia cislo: ' + str(i))
        for seeker in generation:
            solution, fitness = check_solution_and_fitness(start_pos[:], treasures[:], seeker, game_size)
            seeker.fitness = fitness
            
            if seeker.treasures == treasure_count:
                print('Jedinec z ' +str(i) +'. generacie nasiel vsetky poklady, jeho cesta bola: ', solution)
                return
            
            print(seeker.genome, seeker.treasures, seeker.fitness, seeker, seeker.moves)

        
        new_generation = []
        
        
        for j in range(int(N_POPULATION / 2)):
            while True:
                individual1 = tournament(generation, 3)
                individual2 = tournament(generation, 3)
                if not individual1 is individual2:
                    break
            new_children = crossover(individual1, individual2)
            mutate(new_children[0])
            mutate(new_children[1])
            new_generation.append(new_children[0])
            new_generation.append(new_children[1])
        
        """
        while len(new_generation) != N_POPULATION:
            if len(new_generation) < ELITISM_COUNT:
                elites = elitism(generation, ELITISM_COUNT)
                for elite in elites:
                    new_generation.append(elite)
                    print('elites', elite.fitness)
            else:
                seekers = tournament_start(generation, 3)
                new_seekers = crossover(seekers[0], seekers[1])
                mutate(new_seekers[0])
                mutate(new_seekers[1])
                
                if len(new_generation) != N_POPULATION-1:
                    new_generation.append(new_seekers[0])
                    new_generation.append(new_seekers[1])
                else:
                    new_generation.append(new_seekers[0])"""
        
        generation.clear()
        generation.extend(new_generation)
    print()

life_cycle()
