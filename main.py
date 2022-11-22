import itertools as it
import pulp as p
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import math

class Problem():
    def __init__(self):
        self.distance_matrix = []
        self.points          = []
        self.city_to_visit   = []
        self.num_of_cities   = 4
        self.route           = []
        self.first_city      = 0
        self.cost            = None

        self.run()

    def get_data(self):
        try:
            print("ENTER THE NUMBER OF CITIES\nΕισάγετε τον αριθμό των πόλεων που επιθυμείτε να επισκεφθεί ο περιοδεύων πωλητής\nΟι συντεταγμένες των πόλεων θα δημιουργηθούν τυχαία.")
            a = int(input('>> '))
            self.num_of_cities = a

            rnd_x = np.random.randint(0, 100, self.num_of_cities)
            rnd_y = np.random.randint(0, 100, self.num_of_cities)

            self.define_points = pd.DataFrame({
                'x': rnd_x,
                'y': rnd_y,
            })

        except:
            print("ERROR: Εισάγετε ξανά με τον σωστό τρόπο τις απαιτούμενες μεταβλητές.")
            self.get_data()
    
    def build_matrix(self):
        for i in range(self.num_of_cities):
            row = []
            for j in range(self.num_of_cities):
                coords_i = [self.define_points.iloc[i, 0], self.define_points.iloc[i, 1]]
                coords_j = [self.define_points.iloc[j, 0], self.define_points.iloc[j, 1]]
                distance = round(math.dist(coords_i, coords_j), 2)
                row.append(distance)

            self.distance_matrix.append(row)
        
        print("\nDISTANCE MATRIX\nΟι αποστάσεις μεταξύ των πόλεων διαμορφώνονται ως εξής:\n")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.distance_matrix]))

    def naive(self):
        # για 3 πόλεις (self.num_of_cities = 3)
        # τότε perm = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
        perm = list(it.permutations(range(self.num_of_cities)))
        for path in perm:
            cost = 0
            # αποκλείεται κάθε περίπτωση που η πρώτη πόλη 
            # δεν είναι αυτή που έχει οριστεί
            if path[0] == self.first_city:
                for city in path:
                    cost += self.distance_matrix[path[city-1]][path[city]]
                if self.cost == None or cost<self.cost:
                    self.cost  = cost
                    self.route = list(path).append(self.first_city)
        
        return round(self.cost, 2)

    def nearest_neighbor(self):
        self.route = [self.first_city]

        for city in range(self.num_of_cities):
            if city != self.first_city:
                self.city_to_visit.append(city)
        
        i = self.first_city
        while len(self.city_to_visit)!=0:
            row = self.distance_matrix(i)
            for k in sorted(self.route, reverse=True):
                row.pop(k)

            for j in self.city_to_visit:
                if self.distance_matrix[i][j] == min(row):
                    self.route.append(j)
                    self.cost += self.distance_matrix[i][j]
                    self.city_to_visit.remove(j)
                    i = j
                    break

        self.cost += self.distance_matrix[i][self.first_city]
        self.route.append(self.first_city)

    def dynamic(self):

        compare_list = []
        cost_list = []

        def calc_cost(current_city, set_of_cities, cost=0, route=[self.first_city]):
            if len(set_of_cities) == 2:
                for city in set_of_cities:
                    if city != self.first_city:
                        cost = self.distance_matrix[current_city][city] + self.distance_matrix[city][self.first_city]
                        compare_list.append([cost, route+[city, self.first_city]])
            else:
                for city in set_of_cities:
                    if city!=self.first_city:
                        calc_cost(city, set_of_cities-city, cost + self.distance_matrix[current_city][city], route+[city])

                for path in compare_list:
                    cost_list.append(path[0])
                cost = min(cost_list)
                path = compare_list[cost_list.index(cost)]

                cost_list.clear()
                compare_list = [path]

            return path

        min_path = calc_cost(self.first_city, {x for x in range(self.num_of_cities)})
        self.cost = min_path[0]
        round(self.cost, 2)
        self.route = min_path[1]

    def linear(self):
        model = p.LpProblem(name='tsp', sense=1)
    
        f  = []
        c1 = []
        c2 = []
        c3 = []
        c4 = {}
        combinations = list(it.permutations(range(self.num_of_cities), 2))
        for comb in combinations:
            v = p.LpVariable(name=str(comb), lowBound=0, upBound=1, cat='Binary')
            f.append(v*self.distance_matrix[comb[0]][comb[1]])
            
            c1.append(v)
            if comb[0]>len(c2)-1:
                c2.append([v])
            else:
                c2[comb[0]].append(v)

        for i in range(self.num_of_cities):
            c3.append([])
            for v in c1:
                if str(i) in v.name:
                    c3[i].append(v)

        for comb in list(it.combinations(range(self.num_of_cities), 2)):
            c4[comb]=[]
            for v in c1:
                if str(comb[0]) in v.name and str(comb[1]) in v.name:
                    c4[comb].append(v)
                                
        model += p.lpSum(f)

        model += p.LpConstraint(p.lpSum(c1)==self.num_of_cities)
        for group in c2:
            model += p.LpConstraint(p.lpSum(group)==1)
        for group in c3:
            model += p.LpConstraint(p.lpSum(group)==2)
        for group in c4.values():
            model += p.LpConstraint(p.lpSum(group), sense=-1, rhs=1)

        status = model.solve()

        self.cost = round(model.objective.value(), 2)
        self.route = []

        def build_route(city):
            self.route.append(city)
            for var in [v for v in model.variables() if v.value()==1]:
                if city==self.first_city and len(self.route)!=1:
                    return
                elif city==int(var.name[1]):
                    city = int(var.name[4])
                    build_route(city)
                    break
                    


        build_route(self.first_city)
        print(f'cost:{self.cost}\nroute:{self.route}')

    def plot_data(self):
        fig, ax = plt.figure(figsize=(5,5))
        for i, row in self.define_points.iterrows():
            if i == 0:
                ax.scatter(row['x'], row['y'], c='red')
                ax.text(row['x']+1, row['y']+1, 'start')
            else:
                ax.scatter(row['x'], row['y'], c='black')
                ax.text(row['x']+1, row['y']+1, f'{i}')
        
        plt.xlim([-10, 110])
        plt.ylim([-10, 110])
        plt.title('The map of the cities that the travelling salesman will visit')
        
        nodes = [tuple(self.route[i:(i+2)]) for i in range(self.num_of_cities)]
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', edgecolor = 'green')
        for i, j in nodes:
            plt.annotate('', xy = [self.define_points.iloc[j]['x'], self.define_points.iloc[j]['y']], xytext = [self.define_points.iloc[i]['x'], self.define_points.iloc[i]['y']], arrowprops = arrowprops)      
            
        plt.show()


    def run(self):
        print('THE TRAVELLING SALESMAN PROBLEM\n')
        self.get_data()
        self.build_matrix()
        
        
        print("\nCHOOSE SOLUTION\n", '''Πληκτρολογήστε: \n'''
        '''-> 1 (naive) \n'''
        '''-> 2 (nearest neighbor) αν επιθυμείτε το πρόβλημα να λυθεί με τη χρήση προγράμματος, που εντοπίζει τον κοντινότερο γείτονα κάθε σημείου. \n'''
        '''-> 3 (dynamic) αν επιθυμείτε το πρόβλημα να λυθεί με δυναμικό προγραμματισμό\n'''
        '''-> 3 (dynamic) αν επιθυμείτε το πρόβλημα να λυθεί με δυναμικό προγραμματισμό\n'''
        '''-> 4 (linear) αν επιθυμείτε το πρόβλημα να λυθεί με γραμμικό προγραμματισμό\n'''
        )

        while 1:
            sol = int(input('>> '))

            if sol == 1:
                self.naive()
                break
            elif sol == 2:
                self.nearest_neighbor()
                break
            elif sol == 3:
                self.dynamic()
                break
            elif sol == 4:
                self.linear()
                break
            else:
                print("ERROR: Πληκτρολογήστε ξανά τις παραμέτρους που σας ζητήθηκαν, με σωστό τρόπο αυτή τη φορά!")
                continue

        self.plot_data()

if __name__=='__main__':
    pr = Problem()
    pr.run()