import csv
import time
from tqdm import tqdm



if __name__ == '__main__':
    data_file = './WORK_SPACE/data/ETHUSDT.csv'
    csv_reader = csv.reader(open(data_file, 'r'))
    data_list = []
    for _, row in tqdm(enumerate(csv_reader), total=csv_reader.line_num):
        row_list = row[0].split('|')
        time_str = row_list[0]
        time_tuple = time.gmtime(int(time_str))
        row_list[0] = time.strftime('%Y-%m-%d %H:%M:%S', time_tuple)
        row_list.insert(5, row_list[4])
        data_list.append(row_list)

    # write in csv file
    process_data_file = './WORK_SPACE/data/usdt_data.csv'
    with open(process_data_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(['Day', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Taker buy quote asset volume',
        #                  'Taker buy base asset volume', 'Quote asset volume', 'Number of trades', 'Stock Id'])
        # writer.writerows(data_list)
        # filtered data
        writer.writerow(['Day', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        selected_columns = [0, 1, 2, 3, 4, 5, 6]
        filtered_data = []
        for row in tqdm(data_list, total=len(data_list)):
            filtered_row = [row[i] for i in selected_columns]
            filtered_data.append(filtered_row)
        writer.writerows(filtered_data)

        print('Processed data saved in', process_data_file)
        csvfile.close()