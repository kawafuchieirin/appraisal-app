from django import forms

WARD_CHOICES = [
    ('世田谷区', '世田谷区'),
    ('中央区', '中央区'),
    ('中野区', '中野区'),
    ('北区', '北区'),
    ('千代田区', '千代田区'),
    ('台東区', '台東区'),
    ('品川区', '品川区'),
    ('墨田区', '墨田区'),
    ('大田区', '大田区'),
    ('文京区', '文京区'),
    ('新宿区', '新宿区'),
    ('杉並区', '杉並区'),
    ('板橋区', '板橋区'),
    ('江戸川区', '江戸川区'),
    ('江東区', '江東区'),
    ('渋谷区', '渋谷区'),
    ('港区', '港区'),
    ('目黒区', '目黒区'),
    ('練馬区', '練馬区'),
    ('荒川区', '荒川区'),
    ('葛飾区', '葛飾区'),
    ('豊島区', '豊島区'),
    ('足立区', '足立区'),
]

class EstimateForm(forms.Form):
    building_area = forms.FloatField(
        label='建物面積',
        help_text='㎡',
        min_value=10.0,
        max_value=1000.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 80.0'})
    )
    land_area = forms.FloatField(
        label='土地面積',
        help_text='㎡',
        min_value=10.0,
        max_value=2000.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 120.0'})
    )
    building_age = forms.IntegerField(
        label='築年数',
        help_text='年',
        min_value=0,
        max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 10'})
    )
    ward_name = forms.ChoiceField(
        label='区名',
        choices=WARD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        label='査定年',
        initial=2024,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True})
    )
    quarter = forms.ChoiceField(
        label='査定時期',
        choices=[
            (1, '🌸 春（1-3月）'),
            (2, '☀️ 夏（4-6月）'),
            (3, '🍂 秋（7-9月）'),
            (4, '❄️ 冬（10-12月）'),
        ],
        initial=1,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )