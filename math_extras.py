# Calculate an exponential moving average.
def _ema(values, period):
    """Return an EMA series, using ``None`` before the initial average is available."""
    if period <= 0:
        raise ValueError('period must be > 0')

    n = len(values)
    if n == 0:
        return 0

    ema = [None] * n
    smoothing = 2 / (period + 1)

    # Seed with a simple moving average when enough points are available.
    if n >= period:
        seed = sum(values[:period]) / period
        ema[period - 1] = seed
        start = period
    else:
        # Otherwise, use the average of the available values.
        seed = sum(values) / n
        ema[n - 1] = seed
        start = n

    # Compute the remaining EMA values.
    for i in range(start, n):
        ema[i] = (values[i] - ema[i - 1]) * smoothing + ema[i - 1]

    return sum(values[:period]) / len(values[:period])