import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf

# Parameters
n_simulations = 5000
years = 10

number_of_vehicles = 167
avg_cost_per_vehicle = 250000
mean_cost = number_of_vehicles * avg_cost_per_vehicle
initial_cost = np.random.normal(mean_cost, 100000, n_simulations)  # Mean cost and std deviation

annual_cost_per_vehicles = 5300
annual_cost = annual_cost_per_vehicles * number_of_vehicles
annual_operating_cost = np.random.normal(annual_cost, 100000, (n_simulations, years))  # Annual variability

charge_per_ride = 1.86
group1_rides_per_week = 2640 # number of rows in TransportationPeople_Group1 File
group2_rides_per_week = 1205 # number of rows in TransportationPeople_Group2 File
group3_rides_per_week = 2002 # number of rows in TransportationPeople_Group3 File
group4_rides_per_week = 61126 # number of rows in TransportationPeople_Group4 File
rides_per_week = group1_rides_per_week + group2_rides_per_week + group3_rides_per_week + group4_rides_per_week
rides_per_year = rides_per_week * 52
revenue_per_year = rides_per_year * charge_per_ride
annual_revenue = np.random.normal(revenue_per_year, 100000, (n_simulations, years))  # Revenues with high variability

discount_rate = 0.05 # typical discount rate

# Simulation
npv_results = []
for i in range(n_simulations):
    cash_flows = annual_revenue[i] - annual_operating_cost[i]
    cash_flows = np.insert(cash_flows, 0, -initial_cost[i])  # Include initial investment at time 0
    npv = npf.npv(discount_rate, cash_flows)  # Calculate NPV for each simulation
    npv_results.append(npv)

# Analysis
average_npv = np.mean(npv_results)
positive_npv_prob = np.mean(np.array(npv_results) > 0)

# Visualization
plt.figure(figsize=(10, 6))
plt.hist(npv_results, bins=100, color='skyblue', alpha=0.75, edgecolor='black')
plt.title('NPV Distribution from Monte Carlo Simulation')
plt.xlabel('Net Present Value (NPV)')
plt.ylabel('Frequency')
plt.axvline(x=average_npv, color='red', linestyle='dashed', linewidth=1, label=f'Average NPV: ${average_npv:,.2f}')
plt.axvline(x=np.percentile(npv_results, 5), color='green', linestyle='dashed', linewidth=1, label='5th Percentile')
plt.axvline(x=np.percentile(npv_results, 95), color='purple', linestyle='dashed', linewidth=1, label='95th Percentile')
plt.legend()
plt.grid(True)
plt.show()

print(f"Average NPV: ${average_npv:,.2f}")
print(f"Probability of Positive NPV: {positive_npv_prob * 100:.2f}%")