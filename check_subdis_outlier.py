import csv
import numpy as np

SUBDIS_CODE_COL = 4
LATITUDE_COL = 8
LONGITUDE_COL = 9
STDEV_THRESHOLD = 2.5


def read_rows(file):
    with open(file, "r", encoding="utf-8") as buffer:
        reader = csv.reader(buffer)
        rows = [row for row in reader][0:]
        return rows


def dict_by_subdis_code(rows) -> dict[str, list[list[str]]]:
    subdistricts = {}
    for station in rows:
        subdis_code = station[SUBDIS_CODE_COL]
        if subdis_code not in subdistricts:
            subdistricts[subdis_code] = []
        subdistricts[subdis_code].append(station)
    return subdistricts


def warn_subdistrict(rows: list[list[str]], stdev: float) -> list[list[str]]:
    stations = [
        row for row in rows if (row[LATITUDE_COL] != "" and row[LONGITUDE_COL] != "")
    ]
    if len(stations) < 2:
        return []
    else:
        latlon = np.array(
            [
                [float(station[LATITUDE_COL]), float(station[LONGITUDE_COL])]
                for station in stations
            ]
        )

        # Calculate the centroid (mean of all x and y coordinates)
        centroid = np.mean(latlon, axis=0)

        # Calculate the 2D distance of each point from the centroid
        distances = np.linalg.norm(latlon - centroid, axis=1)

        # Calculate the mean and standard deviation of the distances
        mean_distance = np.mean(distances)
        std_dev_distance = np.std(distances)

        # Define the threshold for outliers (mean + standard deviation threshold * standard deviation)
        threshold = mean_distance + stdev * std_dev_distance

        # Filter only outliers stations to warn
        outlier_indices = np.where(distances > threshold)[0]

        return [stations[index] for index in outlier_indices]


def main():
    rows = read_rows("station66_distinct_clean.csv")
    subdistricts = dict_by_subdis_code(rows)
    for subdistrict in subdistricts:
        [
            print(warn)
            for warn in warn_subdistrict(
                subdistricts[subdistrict], stdev=STDEV_THRESHOLD
            )
        ]


if __name__ == "__main__":
    main()
