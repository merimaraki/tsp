import itertools as it

class Problem():
    def __init__(self):
        self.distance_matrix = []
        self.points          = []
        self.city_to_visit   = []
        self.num_of_cities   = None
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

    # def dynamic(self):
    #     set_of_cities = {x for x in range(self.num_of_cities)}

    #     compare_list = []
    #     cost_list = []

    #     def calc_cost(current_city, set_of_cities, cost=0, route=[self.first_city]):


if __name__=='__main__':
    # print(list(it.permutations(range(3))))