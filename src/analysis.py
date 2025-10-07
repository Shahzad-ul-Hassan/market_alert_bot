# 5) range bias
    if avg_pol > 0.2:
        bias = "Likely move towards resistance"
    elif avg_pol < -0.2:
        bias = "Possible test of support"
    else:
        bias = "Range-bound movement expected"

    sr_line = "Technical range unavailable"
    if support is not None and resistance is not None:
        sr_line = f"Support: {support:.0f} | Resistance: {resistance:.0f}"

    return [
        f"Sentiment: {sent_summary}",
        sr_line,
        f"Range: {bias}",
        f"Confidence: {confidence:.1f}%"
    ]
