# Exponential moving average helper
def _ema(values, period):
    """Compute EMA for a list of values.
    Returns a list where entries before enough data are None, and thereafter the EMA values.
    """
    if period <= 0:
        raise ValueError('period must be > 0')
    n = len(values)
    if n == 0:
        return 0

    ema = [None] * n
    smoothing = 2 / (period + 1)

    # seed with simple moving average when enough points exist
    if n >= period:
        seed = sum(values[0:period]) / period
        ema[period-1] = seed
        start = period
    else:
        # not enough points to seed; use average of available as seed
        seed = sum(values) / n
        ema[n-1] = seed
        start = n

    # compute EMA forward
    for i in range(start, n):
        ema[i] = (values[i] - ema[i-1]) * smoothing + ema[i-1]

    return sum(values[0:period]) / len(values[0:period])