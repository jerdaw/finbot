def get_cgr(start_val, end_val, periods) -> float:
    return (end_val / start_val) ** (1 / periods) - 1


if __name__ == "__main__":
    print(get_cgr(100, 110, 1))
