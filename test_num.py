import unittest

import cn2an
import opencc

def num_to_chinese(amount):
    cc = opencc.OpenCC('s2t')  # 's2t' 表示简体转繁体
    simplified_text=cn2an.an2cn(str(amount),"up")
    simplified_text= simplified_text.replace("叁","參")
    return cc.convert(simplified_text)

class TestNumToChinese(unittest.TestCase):
    
    
    def test_thousand(self):
        self.assertEqual(num_to_chinese(22000), "貳萬貳仟")
    
    def test_ten_thousand(self):
        self.assertEqual(num_to_chinese(10000), "壹萬")
    
    def test_two_hundred_twenty_thousand(self):
        self.assertEqual(num_to_chinese(220000), "貳拾貳萬")
    
    def test_large_number(self):
        self.assertEqual(num_to_chinese(3560000), "參佰伍拾陸萬")
    
    def test_one_million(self):
        self.assertEqual(num_to_chinese(1000000), "壹佰萬")
    
    def test_one_hundred_twenty_million(self):
        self.assertEqual(num_to_chinese(120000000), "壹億貳仟萬")

if __name__ == '__main__':
    unittest.main()
