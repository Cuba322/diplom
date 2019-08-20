import json
import sys
import os
import random

#----- Helping functions -----
def show_msg_and_exit(msg):
	print(msg)
	print("Press enter to exit...")
	input()

def fi(x):
	if x < 0:
		return 0
	return x

def alpha_gamma(route, k, mu_dict):
	for i in range(0, len(route)):
		if route[i] == k:
			index = i
			break
	result = 0.
	for i in range(0, index):
		for j in range(index+1, len(route)):
			result += mu_dict.get((route[i],route[j]),0)
	return result

def beta_delta(route, k, mu_dict):
	for i in range(0, len(route)):
		if route[i] == k:
			index = i
			break
	result = 0.
	for j in range(index, len(route)):
			result += mu_dict.get((route[index],route[j]),0)
	return result

def max_profit(mu_dict, T, C):
	return sum(mu_dict.values())*T*C

def is_station_in_fake_routes(k, fake_routes):
	for fr in fake_routes:
		if k in fr:
			return True
	return False

def big_formula_helper1(route, k, l, W, mu_dict):
	part_one = beta_delta(route,k,mu_dict)
	part_two = fi(W*l-alpha_gamma(route,k,mu_dict))
	return fi(part_one-part_two)

def big_formula_helper2(route, fake_routes, l, W, mu_dict):
	result = 0.
	for k in route:
		if is_station_in_fake_routes(k, fake_routes):
			continue
		result += big_formula_helper1(route, k, l, W, mu_dict)
	return result

def big_formula_helper3(routes, ls, fake_routes, W, mu_dict):
	result = 0.
	for i in range(0, len(routes)):
		result += big_formula_helper2(routes[i], fake_routes, ls[i], W, mu_dict)
	return result

def intersection_helper(route1, start_index1, route2, strat_index2):
	result = []
	for i in range(start_index1, len(route1)):
		for j in range(strat_index2, len(route2)):
			if route1[i] == route2[j]:
				result.append( route1[i] )
				result.extend(intersection_helper(route1, i+1, route2, j+1))
				return result
	return result

def is_intersect(route, fake_route):
	if intersection_helper(route, 0, fake_route, 0) == fake_route:
		return True
	return False

def find_real_routes_for_fake_route(routes, fake_route):
	result = []
	for i in range(0, len(routes)):
		if is_intersect(routes[i], fake_route):
			result.append(i)
	return result
			

def big_formula_helper4(routes, ls, fake_route, k, W, mu_dict):
	part_one = 0.
	part_two = 0.
	routes_indexes = find_real_routes_for_fake_route(routes, fake_route)
	gamma = alpha_gamma(fake_route, k, mu_dict)
	delta = beta_delta(fake_route, k, mu_dict)
	for j in routes_indexes:
		alpha = alpha_gamma(routes[j], k, mu_dict)
		beta = beta_delta(routes[j], k, mu_dict)
		part_one += beta-delta
		part_two += fi(W*ls[j]-alpha+gamma)
	part_one += delta
	part_two -= gamma
	return fi(part_one-fi(part_two))

def big_formula_helper5(routes, ls, fake_routes, W, mu_dict):
	result = 0.
	for fake_route in fake_routes:
		for k in fake_route:
			result += big_formula_helper4(routes, ls, fake_route, k, W, mu_dict)
	return result

def big_formula(ns, routes_lengths, routes, fake_routes, W, mu_dict, T, C):
	ls = []
	for i in range(0, len(routes_lengths)):
		ls.append(ns[i]/routes_lengths[i])
	result = big_formula_helper3(routes, ls, fake_routes, W, mu_dict)
	result += big_formula_helper5(routes, ls, fake_routes, W, mu_dict)
	return result*T*C

def find_min_index( cont ):
	result = 0
	for i in range(result, len(cont)):
		if cont[i] < cont[result]:
			result = i
	return result

def find_max_index( cont ):
	result = 0
	for i in range(result, len(cont)):
		if cont[i] > cont[result]:
			result = i
	return result

def normalize_being(n, being):
	s = sum(being)
	for j in range(0, len(being)):
		being[j] = round(being[j]*n/s)
	s = sum(being)
	if s < n:
		min_index = find_min_index(being)
		being[min_index] += (n-s)
	else:
		max_index = find_min_index(being)
		being[max_index] += (s-n)
	return being

def generate_population(n, number_routes, pop_size):
	result = []
	for i in range(0, pop_size):
		being = []
		for j in range(0, number_routes):
			el = random.randint(1,n)
			being.append(el)
		being = normalize_being(n, being)
		result.append(being)
	return result

def mutate_being(n, being, prob):
	for i in range(0, len(being)):
		if random.random() < prob:
			being[i] += random.randint(1,n)
	return normalize_being(n, being)
	
def bread_beings(n, being1, being2):
	result = []
	for i in range(0, len(being1)):
		result.append( (being1[i]+being2[i])/2 )
	return normalize_being(n, result)

#----- Main code -----
if len(sys.argv)<2:
	show_msg_and_exit("Empty argument")
	
file_name = sys.argv[1]
if not os.path.isfile(file_name):
	show_msg_and_exit("Wrong argument")

print("Loading data from file")

with open(file_name, 'r') as in_file:
	data = json.load(in_file)

number_of_vehicles = data['number_of_vehicles']
capacity = data['capacity']
modelling_time = data['modelling_time']
ticket_price = data['ticket_price']
fake_routes =  data['fake_routes']
route_names = []
routes = []
routes_lengths = []

for el in data['routes']:
	route_names.append(el['name'])
	routes.append(el['route'])
	routes_lengths.append(el['route_length'])

mu_dict = {}
for el in data['flows_of_passengers']:
	mu_dict[ tuple(el['indexes']) ] = el['intensity']

print("Loading complete")

def fitnes(ns):
	return big_formula(ns, routes_lengths, routes, 
				  fake_routes, capacity, mu_dict,
				  modelling_time, ticket_price);

prob = 0.3
pop_size = 100
index = round(prob*pop_size)
n = number_of_vehicles
pop = generate_population(number_of_vehicles, len(routes), pop_size)
pop.sort(key=fitnes)
for i in range(0, 100):
	for j in range(index, pop_size):
		being1_index = random.randint(0,index)
		being2_index = random.randint(0,index)
		pop[j] = bread_beings(n, pop[being1_index], pop[being2_index])
		pop[j] = mutate_being(n, pop[j], prob)
	pop.sort(key=fitnes)

solution = big_formula(pop[0], routes_lengths, routes, 
				  fake_routes, capacity, mu_dict,
				  modelling_time, ticket_price)
solution = round(solution)

print('Оптимальное распредление транспорта следующее:\t', pop[0], ' .')
print('При этом потери в прибыли составят: ', solution, ' ,')
max_profit_value = max_profit(mu_dict, modelling_time, ticket_price)
max_profit_value = round(max_profit_value)
print('Максимально вожможная прибыль: ', max_profit_value, ' .')
print()
intervals = []
for i in range(0,len(routes_lengths)):
	intervals.append(routes_lengths[i]/pop[0][i])
print('Интервалы движения по маршрутам: ', intervals, ' .')

show_msg_and_exit("")