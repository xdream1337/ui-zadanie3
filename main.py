import random
from copy import deepcopy

class Seeker():
    def __init__(self, genome, moves, fitness, treasures): 
        self.moves = moves
        self.genome = []
        self.genome.extend(genome)
        self.fitness = fitness
        self.treasures = treasures
    
    def __eq__(self, other): 
        if not isinstance(other, Seeker):
            return NotImplemented

        return self.moves == other.moves and self.genome == other.genome and self.fitness == other.fitness and self.treasures == other.treasures


def mutate(seeker):                                          
    for i in range(64):
        random_num = random.randint(0, 100)
        if random_num < 3:
            seeker.genome[i] = random.randint(0, 255)


def crossover(seeker_1, seeker_2):                                   
    crossover_point = random.randint(0, 63)
    
    genome_1 = []
    genome_2 = []
    
    for i in range(64):
        # zlomovy bod kedy sa menia geny
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
    # kym nenajdem 2 roznych hladacov, robi sa turnaj
    while True:
        seeker_1 = tournament(generation, k)
        seeker_2 = tournament(generation, k)

        if seeker_1 != seeker_2:
            break

    return seeker_1, seeker_2

def elitism(generation, count):
    elites = []

    gen_deepcopy = deepcopy(generation)
    
    # usporiadam generaciu podla fitness
    gen_deepcopy.sort(key=lambda x: x.fitness, reverse=True)

    # vyberem N najlepsich hladacov
    for i in range(count):
        elites.append(gen_deepcopy[i])

    return elites


def count_treasures(seeker, pos, treasures):  
    # prehladavam vsetky poklady a zistujem, ci som nasiel nejaky poklad                  
    for treasure in treasures:
        if pos[0] == treasure[0] and pos[1] == treasure[1]:
            seeker.treasures += 1
            treasures.remove(treasure)
    
    # pokial som nasiel vsetky poklady, vratim true
    if len(treasures) == 0:
        return True


def check_solution_and_fitness(start_pos, treasures, seeker, size): 
    solution = []
    pos = [start_pos[0], start_pos[1]]
    
    # pre kazdy pohyb
    for move in seeker.moves:
        if move == 'H':
            pos[1] -= 1
            # pokial som isiel za pole alebo som nasiel vsetky poklady, skoncim
            if pos[1] < 0 or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'D':
            pos[1] += 1
            # pokial som isiel za pole alebo som nasiel vsetky poklady, skoncim
            if pos[1] > size[1] or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'L':
            pos[0] -= 1
            # pokial som isiel za pole alebo som nasiel vsetky poklady, skoncim
            if pos[0] < 0 or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
        elif move == 'P':
            pos[0] += 1
            # pokial som isiel za pole alebo som nasiel vsetky poklady, skoncim
            if pos[0] > size[0] or count_treasures(seeker, pos, treasures):
                break
            else:
                solution.append(move)
                
    if seeker.treasures > 0:
        seeker.fitness = seeker.treasures - (len(solution)/1000)
    else:
        seeker.fitness -= (len(solution)/1000)
        
    return solution


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
    # zistujem posledne 2 bity genu                        
    move = gene & 3
    
    if move == 0:
        return 'H'
    elif move == 1:
        return 'D'
    elif move == 2:
        return 'L'
    elif move == 3:
        return 'P'


def virtual_machine(genome):   
    index = 0
    moves = []
    
    # vykonam 500 instrukcii
    for i in range(500):
        # posunem 6 bitov doprava, aby mi instrukcia (prve 2 bity) ostala v dekadickom tvare 
        instruction = genome[index] >> 6
        # porovnavam s maskou 63, cim vypocitam adresu
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
            # presiahol som genom
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
                
        generation.append(seeker)
        
    return generation

N_GENERATIONS = int(input('Zadajte pocet generacii: '))
N_POPULATION = int(input('Zadajte pocet hladacov v populacii: '))
ELITISM_COUNT = int(input('Zadajte pocet elit v populacii: '))

def life_cycle():     
    # 1) nacitam subor
    game_size, start_pos, treasures, treasure_count = read_gamefile()
    
    # 2) vytvorim prvu generaciu
    generation = generate_first_population(N_POPULATION)
    max_treasures = 0
    
    for i in range(int(N_GENERATIONS)):
        # vypisujem na konzolu iba kazdu stu generaciu
        
        print('Generacia cislo: ' + str(i+1))
        
        for seeker in generation:
            # 3) kazdemu hladacovi urcim pocet najdenych pokladov a fitness
            solution = check_solution_and_fitness(start_pos[:], treasures[:], seeker, game_size)
            
            #if seeker.treasures > max_treasures:
            #    max_treasures = seeker.treasures
            
            # 4) pozeram sa, ci je hladac, ktory nasiel vsetky poklady
            if seeker.treasures == treasure_count:
                print('Hladac z generacie ' + str(i+1) +'. nasiel vsetky poklady, jeho cesta bola: ', solution)
                return
            
        
        new_generation = []
        
        # pokial je zapnute elitarstvo
        if ELITISM_COUNT > 0:
            # generujem hladacov dokym som nenaplnil generaciu
            while len(new_generation) != N_POPULATION:
                # pokial som este nevybral elity tak ich vyberem a pridam do novej generacie
                if len(new_generation) < ELITISM_COUNT:
                    elites = elitism(generation, ELITISM_COUNT)
                    for elite in elites:
                        new_generation.append(elite)
                else:
                    # 5) turnaj
                    seekers = tournament_start(generation, 3)
                    # 5) krizenie
                    new_seekers = crossover(seekers[0], seekers[1])
                    
                    # 6) mutovanie
                    mutate(new_seekers[0])
                    mutate(new_seekers[1])
                    
                    if len(new_generation) != N_POPULATION-1:
                        new_generation.append(new_seekers[0])
                        new_generation.append(new_seekers[1])
                    else:
                        new_generation.append(new_seekers[0])
        # vypnute elitarstvo
        else:
            seekers = tournament_start(generation, 3)
            new_children = crossover(seekers[0], seekers[1])
            mutate(new_children[0])
            mutate(new_children[1])
            new_generation.append(new_children[0])
            new_generation.append(new_children[1])
        
        # 7)    
        generation.clear()
        generation.extend(new_generation)
    
    print('Ani jeden hladac vo vsetkych generaciach nenasiel poklad.')
    print('Najlepsi vysledok bol:', max_treasures)    

life_cycle()
