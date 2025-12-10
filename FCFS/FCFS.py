# Import function to get CPU time unit for converting time measurements
from cpu_time_unit import get_cpu_time_unit

# Global variable to track total idle time of the CPU
# Idle time occurs when CPU waits for a process to arrive
idle_time = 0


def calculate_waiting_time(n, burst_t, waiting_t, arrival_t):
    """
    Calculate waiting time for each process in FCFS scheduling.

    Args:
        n: Number of processes
        burst_t: List of burst times (execution time needed by each process)
        waiting_t: List to store calculated waiting times (modified in-place)
        arrival_t: List of arrival times for each process
    """
    global idle_time

    # Service time tracks when each process starts execution
    # service_time[i] = time at which process i starts executing
    service_time = [0] * n

    # Calculate waiting time for each process (starting from index 1)
    # Process 0 has waiting time 0 as it arrives first after sorting
    for i in range(1, n):
        # Service time = previous process finish time
        # Previous process finishes at: service_time[i-1] + burst_t[i-1]
        service_time[i] = (service_time[i - 1] + burst_t[i - 1])

        # Waiting time = time process waits before execution starts
        # waiting_t = service_time - arrival_time
        waiting_t[i] = service_time[i] - arrival_t[i]

        # If waiting time is negative, the process arrived after CPU became idle
        # This means CPU had to wait for the process (idle time)
        # Set waiting time to 0 and add idle period to total idle_time
        if waiting_t[i] < 0:
            idle_time += abs(waiting_t[i])  # Track how long CPU was idle
            waiting_t[i] = 0  # Process doesn't wait if CPU is idle


def calculate_turnaround_time(n, burst_t, waiting_t, turn_around_t):
    """
    Calculate turnaround time for each process.
    Turnaround Time = Completion Time - Arrival Time
    Which equals: Burst Time + Waiting Time

    Args:
        n: Number of processes
        burst_t: List of burst times
        waiting_t: List of waiting times (already calculated)
        turn_around_t: List to store turnaround times (modified in-place)
    """
    for i in range(n):
        # Turnaround time = total time from arrival to completion
        turn_around_t[i] = burst_t[i] + waiting_t[i]


def simulate_fcfs_algorithm(data):
    """
    Simulate First Come First Served (FCFS) CPU scheduling algorithm.
    FCFS is a non-preemptive algorithm that executes processes in order of arrival.

    Args:
        data: DataFrame containing process information (process_id, arrival_time, burst_time)

    Returns:
        Dictionary containing scheduling metrics (throughput, CPU utilization, average times)
    """
    # Sort processes by arrival time (essential for FCFS)
    data = data.sort_values('arrival_time')

    # Extract process data from DataFrame
    processes = data['process_id']
    n = len(processes)  # Total number of processes
    burst_time = data['burst_time']  # CPU execution time for each process
    arrival_time = data['arrival_time']  # When each process arrives in ready queue

    # Initialize arrays to store calculated times
    waiting_t = [0] * n  # Time each process waits in ready queue
    turn_around_t = [0] * n  # Total time from arrival to completion

    # Calculate waiting times for all processes
    calculate_waiting_time(n, burst_time, waiting_t, arrival_time)

    # Calculate turnaround times for all processes
    calculate_turnaround_time(n, burst_time, waiting_t, turn_around_t)

    # Calculate aggregate statistics
    total_waiting_t = sum(waiting_t)  # Sum of all waiting times
    total_turn_around_t = sum(turn_around_t)  # Sum of all turnaround times
    total_burst_t = sum(burst_time)  # Total CPU execution time needed

    # CPU Utilization = (Busy Time) / (Total Time including idle)
    # Ratio of time CPU is executing vs total time elapsed
    cpu_utilization = total_burst_t / (total_burst_t + idle_time)

    # Throughput = Number of processes completed per unit time
    # Divide by get_cpu_time_unit() to convert to standard time units
    throughput = n / ((total_burst_t + idle_time) * get_cpu_time_unit())

    # Average Waiting Time = Total waiting time / Number of processes
    # Multiply by get_cpu_time_unit() to convert to standard time units
    average_waiting_time = (total_waiting_t * get_cpu_time_unit()) / n

    # Average Turnaround Time = Total turnaround time / Number of processes
    average_turnaround_time = (total_turn_around_t * get_cpu_time_unit()) / n

    # Display results to console
    print('FCFS algorithm results:')
    print("Throughput = %.4f" % throughput)
    print(f"CPU utilization = {'%.2f' % cpu_utilization}")
    print("Average waiting time = %.4f" % (average_waiting_time))
    print("Average turn around time = %.4f" % (average_turnaround_time))
    # In FCFS, response time equals waiting time (process starts immediately when scheduled)
    print("Average response time = %.4f \n" % (average_waiting_time))

    # Return metrics as a dictionary for UI display or further processing
    return {
        'n': str(n),  # Number of processes
        'throughput': "%.4f" % throughput,  # Processes per time unit
        'cpu_util': "%.2f" % cpu_utilization,  # CPU utilization percentage
        'awt': "%.4f" % (average_waiting_time),  # Average waiting time
        'att': "%.4f" % (average_turnaround_time),  # Average turnaround time
        'art': "%.4f" % (average_waiting_time)  # Average response time (same as waiting time in FCFS)
    }
