from typing import TypeVar

T = TypeVar('T')


def split_collection(collection: list[T], percentages: list[float]) -> list[list[T]]:
    """Split a collection into groups based on the given percentages."""
    if sum(percentages) != 1:
        raise ValueError("Percentages must sum to 1")
    if not all(0 <= p <= 1 for p in percentages):
        raise ValueError("Percentages must be between 0 and 1")

    total = len(collection)
    group_sizes = [round(total * p) for p in percentages]

    # Adjust for rounding errors
    size_difference = total - sum(group_sizes)
    if size_difference != 0:
        exact_sizes = [total * p for p in percentages]
        deviations = [(i, exact_sizes[i] - group_sizes[i]) for i in range(len(percentages))]
        # Sort by largest deviation, break ties by percentages
        deviations.sort(key=lambda x: (abs(x[1]), percentages[x[0]]), reverse=True)

        # Distribute the size difference across groups with the largest deviations
        for i in range(abs(size_difference)):
            index = deviations[i % len(deviations)][0]
            group_sizes[index] += 1 if size_difference > 0 else -1

    groups = []
    start = 0
    for size in group_sizes:
        groups.append(collection[start:start + size])
        start += size

    return groups
