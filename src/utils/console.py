from colorama import Fore, Style


def result_label(row):
    """Visual/colors classification"""
    if row["Error"]:
        return f"{Fore.RED}[ERROR]{Style.RESET_ALL}"

    if row["OK"] and row["Redirected"]:
        return f"{Fore.YELLOW}[REDIRECT]{Style.RESET_ALL}"

    if row["OK"]:
        return f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    return f"{Fore.RED}[BROKEN]{Style.RESET_ALL}"


def print_result(row, only_broken=False):
    """ "Print all the results"""
    is_broken = row["Error"] or not row["OK"]
    if only_broken and not is_broken:
        return

    status = row["Status"] if row["Status"] is not None else "-"
    error = f" | {row['Error']}" if row["Error"] else ""
    final_url = ""
    if row["Redirected"] and row["Final URL"]:
        final_url = f" -> {row['Final URL']}"

    print(
        f"{result_label(row):18} {status!s:>4}  {row['Absolute URL']}{final_url}{error}"
    )
