# Constants
number_of_avs = 167
cost_per_av = 250000
annual_cost_per_av = 5300
cost_per_ride = 2.48
number_of_years = 10

group1_rides_per_week = 2640 # number of rows in TransportationPeople_Group1 File
group2_rides_per_week = 1205 # number of rows in TransportationPeople_Group2 File
group3_rides_per_week = 2002 # number of rows in TransportationPeople_Group3 File
group4_rides_per_week = 61126 # number of rows in TransportationPeople_Group4 File
rides_per_week_per_av = (group1_rides_per_week + group2_rides_per_week + group3_rides_per_week + group4_rides_per_week)/(number_of_avs)

# Calculations
total_initial_cost = number_of_avs * cost_per_av
base_annual_operating_cost = number_of_avs * annual_cost_per_av
annual_revenue_per_av = rides_per_week_per_av * 52 * cost_per_ride
total_annual_revenue = annual_revenue_per_av * number_of_avs

# Adjusting annual costs to include 25% of revenue for additional expenses
additional_annual_costs = total_annual_revenue * 0.25
total_annual_operating_cost = base_annual_operating_cost + additional_annual_costs

# Total revenue and costs over the period
total_revenue_over_period = total_annual_revenue * number_of_years
total_costs_over_period = total_initial_cost + (total_annual_operating_cost * number_of_years)

# ROI calculation
total_net_profit = total_revenue_over_period - total_costs_over_period
roi_with_additional_costs = (total_net_profit / total_initial_cost) * 100

print("The ROI is: ", roi_with_additional_costs)