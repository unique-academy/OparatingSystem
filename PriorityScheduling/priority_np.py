# Import PriorityQueue for managing processes based on priority
from queue import PriorityQueue
# Import function to get CPU time unit for converting time measurements
from cpu_time_unit import get_cpu_time_unit

# Global variable to track total number of processes
n: int
# Global variable to track total idle time of the CPU
# Idle time occurs when CPU waits for a process to arrive
idle_time = 0


def insert_ready_queue(ready_queue, normal_queue, current_time, last_start_time):
    """
    Insert processes that have arrived into the ready queue.
    Processes are added to PriorityQueue which automatically orders them by priority.

    Args:
        ready_queue: PriorityQueue containing processes ready to execute
        normal_queue: Dictionary of processes waiting to arrive
        current_time: Current simulation time (start time for next process)
        last_start_time: Previous start time (when last process started)

    Returns:
        Updated ready_queue with newly arrived processes
    """
    # Check if there are processes waiting to arrive
    if normal_queue:
        # Iterate through all waiting processes
        for value in normal_queue.values():
            # Add process to ready queue if it arrived between last_start_time and current_time
            # This catches all processes that arrived during the current time window
            if last_start_time < value['arrival_time'] <= current_time:
                # PriorityQueue uses tuple's first element (priority) for ordering
                # Lower priority number = higher priority (executed first)
                ready_queue.put((value['priority'],
                                 value['burst_time'],
                                 value['arrival_time'],
                                 value['process_id']))
    return ready_queue


def simulate_priority_np_algorithm(process_data):
    """
    Simulate Priority Non-Preemptive CPU scheduling algorithm.
    Once a process starts executing, it runs to completion without interruption.
    Processes are selected based on priority (lower number = higher priority).

    Args:
        process_data: DataFrame containing process information
                     (process_id, arrival_time, burst_time, priority)

    Returns:
        Dictionary containing scheduling metrics (throughput, CPU utilization, average times)
    """
    global n
    global idle_time

    # Reset idle_time at the start of each algorithm run to avoid accumulation
    idle_time = 0

    # current_time tracks current simulation time (when next process starts)
    current_time = 0
    # last_start_time tracks when the last process started (used to find newly arrived processes)
    last_start_time = -1

    # Add columns to store exit time (completion time) and turnaround time
    process_data['et'] = 0  # Exit time (completion time)
    process_data['tat'] = 0  # Turnaround time

    # Sort processes by arrival time to process them in order
    process_data = process_data.sort_values('arrival_time')

    # Convert DataFrame to dictionary for easier manipulation
    # Each process indexed by its row number
    normal_queue = process_data.to_dict(orient="index")
    n = len(normal_queue)  # Total number of processes

    # PriorityQueue to hold processes ready to execute (sorted by priority)
    ready_queue = PriorityQueue()

    # Main scheduling loop - continues until all processes are executed
    while True:
        # Insert newly arrived processes into ready queue
        ready_queue = insert_ready_queue(ready_queue, normal_queue, current_time, last_start_time)

        # Case 1: Ready queue has processes waiting to execute
        if not ready_queue.empty():
            # Get highest priority process (lowest priority number)
            process = ready_queue.get()

            # Update last_start_time to track when this process starts
            last_start_time = current_time
            # Advance current_time by burst time (process runs to completion)
            current_time += process[1]  # process[1] is burst_time

            # Get process index (process_id - 1 since IDs start at 1)
            k = process[3] - 1  # process[3] is process_id

            # Remove process from normal_queue (it's now completed)
            del normal_queue[k]

            # Record completion time (exit time) for this process
            process_data.at[k, 'et'] = current_time

        # Case 2: Ready queue is empty but processes haven't arrived yet
        elif len(normal_queue) != 0:
            # Get the first process in normal_queue (earliest arrival)
            first_index = next(iter(normal_queue))

            # If CPU is idle (current time < next arrival time)
            if current_time < normal_queue[first_index]['arrival_time']:
                # Calculate and track idle time
                idle_time += normal_queue[first_index]['arrival_time'] - current_time
                # Jump to the arrival time of next process
                current_time = normal_queue[first_index]['arrival_time']

            # Execute the first arrived process
            last_start_time = current_time
            current_time += normal_queue[first_index]['burst_time']
            k = normal_queue[first_index]['process_id'] - 1
            del normal_queue[k]
            process_data.at[k, 'et'] = current_time

        # Case 3: All processes completed (both queues empty)
        elif not normal_queue and ready_queue.empty():
            break

    # Calculate performance metrics
    t_time = calculate_turnaround_time(process_data)
    w_time = calculate_waiting_time(process_data)

    # Display and return results
    return print_data(process_data, t_time, w_time)


def calculate_turnaround_time(process_data):
    """
    Calculate turnaround time for each process.
    Turnaround Time = Completion Time - Arrival Time
    This represents the total time from when a process arrives until it completes.

    Args:
        process_data: DataFrame with process information including exit times

    Returns:
        Average turnaround time across all processes
    """
    total_turnaround_time = 0

    # Calculate turnaround time for each process
    for i in range(n):
        # Turnaround time = completion_time (et) - arrival_time
        turnaround_time = process_data.at[i, 'et'] - process_data.at[i, 'arrival_time']
        total_turnaround_time += turnaround_time
        # Store turnaround time in DataFrame
        process_data.at[i, 'tat'] = turnaround_time

    # Calculate average and convert to standard time units
    average_turnaround_time = (total_turnaround_time * get_cpu_time_unit()) / n

    return average_turnaround_time


def calculate_waiting_time(process_data):
    """
    Calculate waiting time for each process.
    Waiting Time = Turnaround Time - Burst Time
    This represents how long a process waits in the ready queue before executing.

    Args:
        process_data: DataFrame with process information including turnaround times

    Returns:
        Average waiting time across all processes
    """
    total_waiting_time = 0

    # Calculate waiting time for each process
    for i in range(n):
        # Waiting time = turnaround_time - burst_time
        # (Time in system minus time actually executing)
        waiting_time = process_data.at[i, 'tat'] - process_data.at[i, 'burst_time']
        total_waiting_time += waiting_time

    # Calculate average and convert to standard time units
    average_waiting_time = (total_waiting_time * get_cpu_time_unit()) / n

    return average_waiting_time


def print_data(process_data, average_turnaround_time, average_waiting_time):
    """
    Display scheduling algorithm results and return metrics dictionary.
    Calculates and prints CPU utilization, throughput, and average times.

    Args:
        process_data: DataFrame with all process information
        average_turnaround_time: Calculated average turnaround time
        average_waiting_time: Calculated average waiting time

    Returns:
        Dictionary containing all scheduling metrics for UI display
    """
    # Calculate total CPU burst time (sum of all process execution times)
    total_burst_t = process_data['burst_time'].sum(axis=0)

    # CPU Utilization = (Busy Time) / (Total Time including idle)
    # Represents the percentage of time CPU is actively executing processes
    cpu_utilization = total_burst_t / (total_burst_t + idle_time)

    # Throughput = Number of processes completed per unit time
    # Divide by get_cpu_time_unit() to convert to standard time units
    throughput = n / ((total_burst_t + idle_time) * get_cpu_time_unit())

    # Display results to console
    print('Priority non preemptive algorithm results: ')
    print("Throughput = %.4f" % throughput)
    print(f"CPU utilization = {cpu_utilization}")
    print(f'Average waiting time = {"%.2f" % average_waiting_time}')
    print(f'Average turn around time = {"%.2f" % average_turnaround_time}')
    # In non-preemptive scheduling, response time equals waiting time
    # (process starts executing as soon as it's selected)
    print(f'Average response time = {"%.2f" % average_waiting_time}\n')

    # Return metrics as dictionary for UI display or further processing
    return {
        'n': str(n),  # Number of processes
        'throughput': "%.4f" % throughput,  # Processes completed per time unit
        'cpu_util': "%.2f" % cpu_utilization,  # CPU utilization percentage
        'awt': "%.4f" % average_waiting_time,  # Average waiting time
        'att': "%.4f" % average_turnaround_time,  # Average turnaround time
        'art': "%.4f" % average_waiting_time  # Average response time (same as waiting time in non-preemptive)
    }
