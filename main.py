from modules import sqlite_helper

def main():
    csv_file = r"./data/test.csv"
    # sqlite_helper.load_csv_and_insert(csv_file)
    print(sqlite_helper.select_columns_from_db(["measurement_time", "channel_1", "channel_2"]))

if __name__ == "__main__":
    main()