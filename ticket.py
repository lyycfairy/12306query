# coding: utf-8
"""Train tickets query via command-line.

Usage:
   tickets [-gdtkz] <from> <to> <date>

Options:
   -h,--help   显示帮助菜单
   -g          高铁
   -d          动车
   -t          特快
   -k          快速
   -z          直达

Example:
   python3 tickets.py shanghai beijing 2017-12-12
"""
from docopt import docopt
from parse_stations import stations,c_stations
from prettytable import PrettyTable
import prettytable
import requests
import re

#用于组合多个.*?正则表达式，代表爬取的不同座位余票信息
def generate_string(str, times):
    ret = ''
    for i in range(0, times):
        ret += str
    return ret

#生成PrettyTable,用于输出表格
def get_my_table(header):
    pt = PrettyTable(header)
    pt.hrules = prettytable.ALL
    return pt

def cli():
    """command-line interface"""
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])  #把用户输入的全拼地址名转换为12306用的三字母地址名
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']

    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&' \
          'leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(date, from_station, to_station)
    response = requests.get(url, verify=False)
    text = response.json()['data']['result']    #通过浏览器的开发者工具可以看到，返回的信息都存在result中

    #不同位置的余票信息，不是按规则排列的，所以需要手动指定位置
    seat_dict = {
        '商务座' : 13,
        '一等座' : 12,
        '二等座' : 11,
        '高级软卧' : 2,
        '软卧' : 4,
        '动卧' : 14,
        '硬卧' : 9,
        '硬座' : 10,
        '无座' : 7
    }

    match_date = date.split('-')[0] + '\d{4}' #把日期改成年+4位数字，因为部分车次可能运行超过1-2天！！！
    match_seat = generate_string('(.*?)\|', 14) #用于显示不同座位的余票信息有14个位置，先全部爬下来

    header = '车次 出发站 到达站 发车时间 到达时间 持续时间 商务座 一等座 二等座 高级软卧 软卧 动卧 硬卧 硬座 无座'.split()
    pt = get_my_table(header)
    for str in text:
        to_match = '\|([GDKTZ]?\d{1,4})\|.*?\|.*?\|(\w+)\|(\w+)\|(.*?)\|(.*?)\|(.*?)\|.*' + match_date +  \
                   '\|.*?\|.*?\|.*?\|.*?\|.*?\|.*?\|' + match_seat

        pattern = re.compile(to_match)
        result = re.findall(pattern,str)
        result = list(result[0])
        result[1] = c_stations.get(result[1])   #将12306的内部地址名转为中文名
        result[2] = c_stations.get(result[2])

        data = result[:6]   #前6项与header对应，直接拷贝
        for index in seat_dict.values():
            if result[index+5] == '':
                result[index+5] = '--'
            data.append(result[index+5])    #按照自己统计的位置计入不同位置的余票信息
        pt.add_row(data)


    print(pt)

if __name__ == '__main__':
    cli()