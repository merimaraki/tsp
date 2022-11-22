import itertools as it
import pulp as p

class Problem():
    def __init__(self):
        self.distance_matrix = [[0, 10, 15, 20],
                                [10, 0, 35, 25],
                                [15, 35, 0, 30],
                                [20, 25, 30, 0]]
        self.points          = []
        self.city_to_visit   = []
        self.num_of_cities   = 4
        self.route           = []
        self.first_city      = 0
        self.cost            = None

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

if __name__=='__main__':
    pr = Problem()
    pr.linear()