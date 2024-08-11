import numpy as np

def simulate_stochastic_process(mu: float, sigma: float, X0:float , arrival_times: np.ndarray):
    '''
    Simulates a stochastic process with given parameters.
    '''

    dt = np.diff(arrival_times, prepend=0)  # Append 0 at the start for correct dimensions
    dW = np.random.normal(0, np.sqrt(dt))
    X = np.zeros_like(arrival_times)
    X[0] = X0
    X[1:] = X0 * np.cumprod(1 + mu * dt[1:] + sigma * dW[1:])
    return X

def generate_poisson_arrivals(lambda_param, T):
    '''
    Generate the arrival times
    '''
    num_arrivals = np.random.poisson(lambda_param * T)
    inter_arrival_times = np.random.exponential(1 / lambda_param, num_arrivals)
    arrival_times = np.cumsum(inter_arrival_times)
    return np.insert(arrival_times, 0, 0)

def smallest_divisor(number, divisor)-> int:
    if divisor == 0:
        raise ValueError("Divisor cannot be zero")
    return int((number // divisor) * divisor)