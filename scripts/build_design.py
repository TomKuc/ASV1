#!/usr/bin/env python3
"""Generate the review-stage KiCad schematic. No manufacturing exports.

All generated objects have stable UUIDs. This is a third-party generator,
not a substitute for opening the project and running KiCad ERC/DRC.
"""
from pathlib import Path
import csv
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / 'hardware'
PROJECT = 'Ankle_Sensor_V1'
NS = uuid.UUID('a576ae42-ebca-47f8-943c-cdb72f4c6ed7')

def uid(key):
    return str(uuid.uuid5(NS, key))

def q(s):
    return json.dumps(str(s), ensure_ascii=False)

def effects(size=1.0, justify='', hide=False):
    return f'(effects (font (size {size} {size}))' + (f' (justify {justify})' if justify else '') + (' hide' if hide else '') + ')'

def prop(key, value, x, y, hide=False, size=1):
    return f'(property {q(key)} {q(value)} (at {x} {y} 0) {effects(size, hide=hide)})'

SYMS = {}
def symbol(name, left, right=(), width=20.32, passive=False):
    """Pin list entries: (number, name, electrical type). Coordinates in library space."""
    pins = []
    rows = max(len(left), len(right), 2)
    height = (rows + 1) * 2.54
    for side, entries in [('left', left), ('right', right)]:
        for i, (num, pname, typ) in enumerate(entries):
            y = ((len(entries)-1)/2-i)*2.54
            x = -(width/2+2.54) if side == 'left' else width/2+2.54
            pins.append(dict(num=str(num), name=pname, type=typ, x=round(x,5), y=round(y,5), angle=0 if side=='left' else 180, side=side))
    SYMS[name] = dict(name=name, width=width, height=height, pins=pins, passive=passive)

P = 'passive'
BI = 'bidirectional'
PI = 'power_in'
symbol('R', [(1,'',P)], [(2,'',P)], 5.08, True)
symbol('C', [(1,'',P)], [(2,'',P)], 5.08, True)
symbol('LED', [(1,'K',P)], [(2,'A',P)], 7.62, True)
symbol('Switch', [(1,'',P)], [(2,'',P)], 5.08, True)
symbol('Crystal', [(1,'',P)], [(2,'',P)], 7.62, True)
symbol('TestPoint', [(1,'TP',P)], width=2.54)
symbol('PWR_FLAG', [(1,'pwr','power_out')], width=2.54)
symbol('Battery_3wire', [(1,'PACK+',P),(2,'NTC',P),(3,'PACK-',P)], width=15.24)
symbol('SWD_6pad', [(1,'VTref',P),(2,'SWDIO',P),(3,'GND',P)], [(4,'SWCLK',P),(5,'nRESET',P),(6,'GND',P)], 17.78)
symbol('BQ25185DLHR', [(10,'IN',PI),(2,'BAT',P),(6,'TS/MR','input'),(7,'ILIM/VSET',P),(8,'ISET',P),(5,'GND',PI),(11,'EP_GND',PI)], [(1,'SYS','power_out'),(4,'nCE','input'),(9,'STAT1','open_collector'),(3,'STAT2','open_collector')], 25.4)
symbol('TPS7A2030PDBVR', [(1,'IN',PI),(3,'EN','input'),(2,'GND',PI)], [(5,'OUT','power_out'),(4,'NC','no_connect')], 22.86)
symbol('LSM6DSV32XTR', [(8,'VDD',PI),(5,'VDD_IO',PI),(12,'nCS','input'),(13,'SCK','input'),(14,'SDI','input'),(2,'SDx_Qvar1',BI),(3,'SCx_Qvar2',BI),(6,'GND',PI),(7,'GND',PI)], [(1,'SDO','output'),(4,'INT1','output'),(9,'INT2_DEN',BI),(10,'OCS_Aux','input'),(11,'SDO_Aux',BI)], 27.94)
symbol('Serial_NOR_WSON8', [(8,'VCC',PI),(1,'nCS','input'),(6,'CLK','input'),(5,'IO0',BI),(2,'IO1',BI)], [(3,'IO2',BI),(7,'IO3',BI),(4,'GND',PI),(9,'EP',P)], 22.86)
symbol('USB_C_USB2', [('A1','GND',P),('A4','VBUS',P),('A5','CC1',P),('A6','D+',P),('A7','D-',P),('A8','SBU1',P),('A9','VBUS',P),('A12','GND',P)], [('B1','GND',P),('B4','VBUS',P),('B5','CC2',P),('B6','D+',P),('B7','D-',P),('B8','SBU2',P),('B9','VBUS',P),('B12','GND',P),('SH','SHIELD',P)], 22.86)
symbol('USBLC6_2SC6', [(1,'IO1',P),(3,'IO2',P),(2,'GND',PI)], [(6,'IO1',P),(4,'IO2',P),(5,'VBUS',PI)], 20.32)
symbol('TLV7042DGKR', [(8,'VCC',PI),(3,'INA+', 'input'),(2,'INA-', 'input'),(5,'INB+', 'input'),(6,'INB-', 'input'),(4,'GND',PI)], [(1,'OUTA','open_collector'),(7,'OUTB','open_collector')], 22.86)
symbol('AO3400A', [(1,'G','input')], [(3,'D',P),(2,'S',P)], 10.16)
symbol('TLV803EA26DBZR', [(3,'VDD',PI),(1,'GND',PI)], [(2,'nRESET','open_collector')], 20.32)
for sn in ['R','Switch']:
    SYMS[sn]['height']=2.54
SYMS['C']['height']=3.81

module_names = ['GND','GND','P1.10','P1.11','P1.12','P1.13','P1.14','P1.15','P0.03','P0.29','P0.02','P0.31','P0.28','P0.30','GND','P0.27','P0.00_XL1','P0.01_XL2','P0.26','P0.04','P0.05','P0.06','P0.07','P0.08','P1.08','P1.09','P0.11','VDD','P0.12','VDDH','DCCH','VBUS','GND','D-','D+','P0.14','P0.13','P0.16','P0.15','P0.18_nRESET','P0.17','P0.19','P0.21','P0.20','P0.23','P0.22','P1.00','P0.24','P0.25','P1.02','SWDIO','P0.09_NFC1','SWDCLK','P0.10_NFC2','GND','P1.04','P1.06','P1.07','P1.05','P1.03','P1.01']
def mod_type(name):
    return PI if name in ('GND','VDD','VDDH','VBUS') else BI
symbol('MDBT50Q_P1MV2_VerL', [(i+1,n,mod_type(n)) for i,n in enumerate(module_names[:31])], [(i+32,n,mod_type(n)) for i,n in enumerate(module_names[31:])], 43.18)

COMPONENTS=[]
def add(ref, sym, value, pins, sheet, x, y, mpn='', jlc='', footprint='', status='REVIEW', note='', populate=True):
    COMPONENTS.append(dict(ref=ref, symbol=sym, value=value, pins={str(k):v for k,v in pins.items()}, sheet=sheet, x=x, y=y, mpn=mpn, jlcpcb=jlc, footprint=footprint, status=status, note=note, populate=populate, uuid=uid(ref)))

RCOUNT=0
CCOUNT=0
def resistor(value, a,b,sheet,x,y,mpn='',jlc='',note=''):
    global RCOUNT
    RCOUNT+=1
    add(f'R{RCOUNT}','R',value,{1:a,2:b},sheet,x,y,mpn,jlc,'Resistor_SMD:R_0402_1005Metric',note=note)
def cap(value,a,b,sheet,x,y,mpn='',jlc='',size='0402',note=''):
    global CCOUNT
    CCOUNT+=1
    add(f'C{CCOUNT}','C',value,{1:a,2:b},sheet,x,y,mpn,jlc,f'Capacitor_SMD:C_{size}_'+('1005Metric' if size=='0402' else '1608Metric'),note=note)
def tp(ref,net,sheet,x,y):
    add(ref,'TestPoint',net,{1:net},sheet,x,y,footprint='TestPoint:TestPoint_Pad_D1.0mm',status='NOT_ASSEMBLED',populate=False)

# Draft power path with hardware temperature and supply-valid inhibition.
add('U1','BQ25185DLHR','BQ25185DLHR',{10:'VBUS',2:'VBAT',6:'NTC_TS',7:'CHG_ILIM',8:'CHG_ISET',5:'GND',11:'GND',1:'VSYS',4:'CHG_CE_N',9:'CHG_STAT1_N',3:'CHG_STAT2_N'},'power',75,60,'BQ25185DLHR','C19725033',note='Independent TLV7042 NTC window controls CE; qualify actual battery and startup')
add('U2','TPS7A2030PDBVR','TPS7A2030PDBVR',{1:'VSYS',3:'VSYS',2:'GND',5:'+3V0',4:None},'power',255,60,'TPS7A2030PDBVR','C963429','Package_TO_SOT_SMD:SOT-23-5')
add('J2','Battery_3wire','PROTECTED_1S_4V2_NTC',{1:'VBAT',2:'NTC_TS',3:'GND'},'power',75,125,note='Connector and pack MPN pending; NTC must physically contact cell')
resistor('24k 1%','CHG_ILIM','GND','power',170,95,note='BQ25185: 4.2V / 100mA input limit')
resistor('2k 1%','CHG_ISET','GND','power',170,120,note='150mA programmed; actual current constrained by 100mA input and load')
resistor('100k 1%','VSYS','CHG_CE_N','power',170,145,note='CE defaults HIGH without a valid3V-powered temperature window')
resistor('10k 1%','+3V0','CHG_STAT1_N','power',270,120)
resistor('10k 1%','+3V0','CHG_STAT2_N','power',270,145)
cap('1u 16V X7R','VBUS','GND','power',75,180,size='0603',note='USB input total capacitance must remain within USB inrush specification')
cap('10u 10V X5R','VSYS','GND','power',170,180,size='0603',note='Ensure effective capacitance >=1uF at4.5V')
cap('1u 10V X7R','VBAT','GND','power',270,180,size='0603')
cap('2.2u 10V X5R','VSYS','GND','power',170,210,size='0603',note='Local LDO input; include in effective USB inrush analysis')
cap('10u 10V X5R','+3V0','GND','power',270,210,size='0603',note='LDO local output; validate DC bias, transient and ESR')
resistor('1M 1%','VBAT','VBAT_ADC','power',75,240)
resistor('1M 1%','VBAT_ADC','GND','power',170,240)
cap('100n 10V X7R','VBAT_ADC','GND','power',270,240,note='SAADC acquisition >=40us; divider tau50ms')
for i,(net,x) in enumerate([('VBUS',50),('VBAT',100),('GND',150)]):
    add(f'#FLG{i+1:02d}','PWR_FLAG','PWR_FLAG',{1:net},'power',x,265,status='VIRTUAL',populate=False)
for i,(net,x,y) in enumerate([('VSYS',210,265),('+3V0',345,95),('VBAT',345,180),('GND',345,210)]):tp(f'TP{i+1}',net,'power',x,y)

mp={str(i):None for i in range(1,62)}
mp.update({str(i):'GND' for i in [1,2,15,33,55]})
mp.update({'3':'LED_K','4':'USER_BTN_N','5':'CHG_STAT1_N','6':'CHG_STAT2_N','7':'CHG_INHIBIT','11':'VBAT_ADC','17':'LF_XL1','18':'LF_XL2','27':'IMU_INT1','28':'+3V0','29':'IMU_INT2','30':'+3V0','32':'VBUS','34':'USB_DN','35':'USB_DP','36':'IMU_MOSI','37':'IMU_SCK','38':'IMU_CS_N','39':'IMU_MISO','40':'RESET_N','41':'FLASH_CS_N','42':'QSPI_SCK','43':'QSPI_IO1','44':'QSPI_IO0','45':'QSPI_IO3','46':'QSPI_IO2'})
mp.update({'51':'SWDIO','53':'SWCLK'})
add('U3','MDBT50Q_P1MV2_VerL','MDBT50Q-P1MV2',mp,'mcu',85,110,'MDBT50Q-P1MV2','C5119772',note='DCCH31 provisionally NC in normal voltage mode; visually verify8.3. Footprint unresolved. P1.14 HIGH inhibits charging throughQ2')
add('Y1','Crystal','32.768kHz CL7pF',{1:'LF_XL1',2:'LF_XL2'},'mcu',255,50,'ABS07-32.768KHZ-7-T',note='Candidate MPN; verify ESR and LFXO load before production')
cap('10p C0G DRAFT','LF_XL1','GND','mcu',205,85,note='CL=7pF with assumed2pF stray; tune after parasitic review')
cap('10p C0G DRAFT','LF_XL2','GND','mcu',305,85,note='Provisional load capacitor; not a verified oscillator design')
cap('4.7u 10V X5R','+3V0','GND','mcu',205,125,size='0603')
cap('100n 10V X7R','+3V0','GND','mcu',305,125)
cap('4.7u 10V X5R','VBUS','GND','mcu',205,165,size='0603',note='Confirm against Raytac USB reference before release')
resistor('10k 1%','+3V0','RESET_N','mcu',305,165)
tp('TP5','RESET_N','mcu',255,205)

add('U4','LSM6DSV32XTR','LSM6DSV32XTR',{1:'IMU_MISO',2:'GND',3:'GND',4:'IMU_INT1',5:'+3V0',6:'GND',7:'GND',8:'+3V0',9:'IMU_INT2',10:'+3V0',11:None,12:'IMU_CS_N',13:'IMU_SCK',14:'IMU_MOSI'},'sensors',75,60,'LSM6DSV32XTR','C22461202',note='SDO_Aux11 NC permitted by ST main-SPI mode. Disabled Qvar pins2/3 tiedGND perDS; ERC pin-type warnings reviewed')
add('U5','Serial_NOR_WSON8','W25Q01JVZEIQ_128MiB',{1:'FLASH_CS_N',2:'QSPI_IO1',3:'QSPI_IO2',4:'GND',5:'QSPI_IO0',6:'QSPI_CLK_FLASH',7:'QSPI_IO3',8:'+3V0',9:'GND'},'sensors',270,60,'W25Q01JVZEIQ','C5137036',note='128MiB dual-die. Firmware EN4B+per-die BUSY/state handling required. EP/paste geometry review pending')
cap('100n 10V X7R','+3V0','GND','sensors',65,115,note='Within few mm of IMU VDD8')
cap('100n 10V X7R','+3V0','GND','sensors',165,115,note='Within few mm of IMU VDD_IO5')
cap('1u 10V X7R','+3V0','GND','sensors',65,150)
cap('100n 10V X7R','+3V0','GND','sensors',270,115,note='Flash VCC local')
cap('4.7u 10V X5R','+3V0','GND','sensors',270,150,size='0603')
resistor('100k 1%','+3V0','IMU_CS_N','sensors',65,195)
resistor('100k 1%','+3V0','FLASH_CS_N','sensors',270,195)
resistor('22R 1% DRAFT','QSPI_SCK','QSPI_CLK_FLASH','sensors',270,230,note='Place at MCU source; tune0-33ohm by measurement')
resistor('100k 1%','+3V0','QSPI_IO2','sensors',65,230)
resistor('100k 1%','+3V0','QSPI_IO3','sensors',165,230)
tp('TP6','IMU_INT1','sensors',65,270)
tp('TP7','IMU_INT2','sensors',165,270)

usb={k:'GND' for k in ['A1','A12','B1','B12','SH']}
usb.update({k:'VBUS' for k in ['A4','A9','B4','B9']})
usb.update({'A5':'USB_CC1','B5':'USB_CC2','A6':'USB_DP_CONN','B6':'USB_DP_CONN','A7':'USB_DN_CONN','B7':'USB_DN_CONN','A8':None,'B8':None})
add('J1','USB_C_USB2','TYPE-C-31-M-12',usb,'io',65,65,'TYPE-C-31-M-12','C165948',note='Logical contact names; physical combined pads and anchor mapping not yet verified')
add('U6','USBLC6_2SC6','USBLC6-2SC6',{1:'USB_DP_CONN',6:'USB_DP',3:'USB_DN_CONN',4:'USB_DN',2:'GND',5:'VBUS'},'io',270,65,'USBLC6-2SC6','C7519','Package_TO_SOT_SMD:SOT-23-6',note='Flow-through protection: do not join across PCB route bypassing package')
resistor('5.1k 1%','USB_CC1','GND','io',65,120)
resistor('5.1k 1%','USB_CC2','GND','io',165,120)
add('J3','SWD_6pad','SWD_POGO_6',{1:'+3V0',2:'SWDIO',3:'GND',4:'SWCLK',5:'RESET_N',6:'GND'},'io',270,135,note='VTref sense only; programmer must not back-power3V',populate=False)
add('SW1','Switch','USER_BUTTON',{1:'USER_BTN_N',2:'SW_RETURN'},'io',65,175,note='R25 limits100nF discharge current through contact to about3mA')
resistor('100k 1%','+3V0','USER_BTN_N','io',165,175)
cap('100n 10V X7R','USER_BTN_N','GND','io',65,210)
add('D1','LED','GREEN_LED',{1:'LED_K',2:'LED_A'},'io',270,210,note='Low current LED; MPN pending')
resistor('2.2k 1%','+3V0','LED_A','io',165,210)
tp('TP8','NTC_TS','power',345,125)
tp('TP9','CHG_ALLOW_H','power',345,145)

# Independent battery-temperature hardware inhibit; Q2 isolates the MCU so it
# cannot pull the hardware allow node HIGH. U8 inhibits before references settle.
add('U7','TLV7042DGKR','TLV7042DGKR',{8:'+3V0',3:'NTC_TS',2:'NTC_REF_HOT',5:'NTC_REF_COLD',6:'NTC_TS',4:'GND',1:'CHG_ALLOW_H',7:'CHG_ALLOW_H'},'temperature',75,65,'TLV7042DGKR','C2760466','Package_SO:VSSOP-8_3x3mm_P0.65mm',note='C number verified atLCSC only; JLC procurement remains open')
add('Q1','AO3400A','AO3400A',{1:'CHG_ALLOW_H',3:'CHG_CE_N',2:'GND'},'temperature',275,65,'AO3400A','C20917','Package_TO_SOT_SMD:SOT-23')
resistor('100k 0.1%','+3V0','NTC_REF_HOT','temperature',65,125,note='Includes supply brownout down to supervisor minimum threshold; do not substitute1%')
resistor('10k 0.1%','NTC_REF_HOT','GND','temperature',165,125)
resistor('27.4k 0.1%','+3V0','NTC_REF_COLD','temperature',65,165)
resistor('10k 0.1%','NTC_REF_COLD','GND','temperature',165,165)
resistor('100k 1%','+3V0','CHG_ALLOW_H','temperature',275,125,note='Gate voltage min>2.5V with1Mdown and valid3V; battery-only bias current~30uA')
resistor('1M 1%','CHG_ALLOW_H','GND','temperature',275,165)
cap('100n 10V X7R','+3V0','GND','temperature',275,210,note='Comparator local bypass')
add('U8','TLV803EA26DBZR','TLV803EA26DBZR',{3:'+3V0',1:'GND',2:'CHG_ALLOW_H'},'temperature',75,210,'TLV803EA26DBZR','C1852119','Package_TO_SOT_SMD:SOT-23',note='2.64V supervisor, activeLOW open-drain, nominal200ms delay; check exact suffix/pinout')
add('Q2','AO3400A','AO3400A',{1:'CHG_INHIBIT',3:'CHG_ALLOW_H',2:'GND'},'temperature',365,65,'AO3400A','C20917','Package_TO_SOT_SMD:SOT-23',note='MCU HIGH inhibits; cannot override comparator/supervisorLOW')
resistor('100k 1%','CHG_INHIBIT','GND','temperature',165,250,note='Q2 defaultsOFF with GPIOHiZ')
cap('100n 10V X7R','+3V0','GND','temperature',165,210,note='Supervisor local bypass')
resistor('1k 1%','SW_RETURN','GND','io',165,250,note='Limits current from C17 through closed switch; LOW still~30mV')

# Procurement references are documented in docs/passives_sourcing.md.
# A catalog C number alone is deliberately not called a PCBA stock reservation.
R_PARTS={
 ('24k','1%'):('0402WGF2402TCE','C25769','LCSC_ONLY_PROCUREMENT_REVIEW'),
 ('2k','1%'):('RC0402FR-072KL','C60488','REVIEW'),
 ('100k','1%'):('0402WGF1003TCE','C25741','REVIEW'),
 ('10k','1%'):('0402WGF1002TCE','C25744','REVIEW'),
 ('1M','1%'):('0402WGF1004TCE','C26083','REVIEW'),
 ('22R','1%'):('0402WGF220JTCE','C25092','REVIEW'),
 ('5.1k','1%'):('0402WGF5101TCE','C25905','REVIEW'),
 ('2.2k','1%'):('0402WGF2201TCE','C25879','REVIEW'),
 ('10k','0.1%'):('RT0402BRD0710KL','C190095','REVIEW'),
 ('27.4k','0.1%'):('RT0402BRD0727K4L','C852679','LCSC_ONLY_PROCUREMENT_REVIEW'),
 ('100k','0.1%'):('ERA2AEB104X','C445619','REVIEW'),
 ('1k','1%'):('0402WGF1001TCE','C11702','REVIEW'),
}
DATASHEETS={
 'BQ25185DLHR':'https://www.ti.com/lit/ds/symlink/bq25185.pdf',
 'TPS7A2030PDBVR':'https://www.ti.com/lit/ds/symlink/tps7a20.pdf',
 'MDBT50Q-P1MV2':'https://www.raytac.com/tw/download/index.php?index_id=24',
 'LSM6DSV32XTR':'https://www.st.com/resource/en/datasheet/lsm6dsv32x.pdf',
 'W25Q01JVZEIQ':'https://www.mouser.com/datasheet/2/949/Winbond_Electronics_Corporation_09_06_2024_W25Q01J-3501286.pdf',
 'USBLC6-2SC6':'https://www.st.com/resource/en/datasheet/usblc6-2.pdf',
 'TLV7042DGKR':'https://www.ti.com/lit/gpn/TLV7042',
 'TLV803EA26DBZR':'https://www.ti.com/lit/ds/symlink/tlv803e.pdf',
 'AO3400A':'https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf',
 'TYPE-C-31-M-12':'https://datasheet.lcsc.com/lcsc/1903211732_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf',
}
for c in COMPONENTS:
    # KiCad's electrical connection grid is 50mil. Library pins are on this
    # grid too; snapping the symbol origin avoids misleading off-grid wires.
    c['x']=round(round(c['x']/1.27)*1.27,5)
    c['y']=round(round(c['y']/1.27)*1.27,5)
    if c['symbol']=='R':
        bits=c['value'].split()
        c['mpn'],c['jlcpcb'],c['status']=R_PARTS[(bits[0],bits[1])]
    if c['symbol']=='C':
        v=c['value'].split()[0]
        if v=='100n':
            c['value']='100n 16V X7R';c['mpn']='CL05B104KO5NNNC';c['jlcpcb']='C1525'
        elif v=='1u':
            c['value']='1u 16V X7R';c['mpn']='CC0603KRX7R7BB105';c['jlcpcb']='C106248';c['footprint']='Capacitor_SMD:C_0603_1608Metric'
        elif v=='10u':c['mpn']='CL10A106KP8NNNC';c['jlcpcb']='C19702'
        elif v=='4.7u':c['mpn']='CL10A475KP8NNNC';c['jlcpcb']='C1705'
        elif v=='2.2u':c['value']='2.2u 16V X5R';c['mpn']='CL10A225KO8NNNC';c['jlcpcb']='C23630'
        elif v=='10p':c['value']='10p 50V C0G DRAFT';c['mpn']='CL05C100JB5NNNC';c['jlcpcb']='C32949'
    c['datasheet']=DATASHEETS.get(c['mpn'],'')
    choices_path=HW/'component_choices.json'
    if choices_path.exists():
        overrides=json.loads(choices_path.read_text()).get(c['ref'],{})
        c.update(overrides)

NOTES={
 'power': [('POWER PATH / BATTERY - REVIEW DRAFT',25,17),('4.2V protected1S pack only. 100mA USB input limit. 150mA ISET is dynamically reduced.',25,25),('See temperature sheet for independent NTC window. Pack/NTC qualification is mandatory.',25,33)],
 'mcu': [('MCU / RADIO / CLOCK - REVIEW DRAFT',25,17),('Normal voltage: VDD=VDDH=3V0. DCCH reference wiring is a release blocker.',25,25),('QSPI/SPI on fast P0 GPIO. See pinmap.csv. No antenna geometry has been guessed.',25,33),('LFXO loads and USB bypass capacitors are provisional pending reference circuit review.',185,235)],
 'sensors': [('IMU / NOR FLASH - REVIEW DRAFT',25,17),('SPI8MHz; INT1 FIFO watermark; INT2 can serve timestamp/ODR-trigger experiments.',25,25),('U5 upgraded to128MiB, same8x6mm body. Address32bit and dual-die status handling.',25,33)],
 'io': [('USB2 / USER INTERFACE / SWD - REVIEW DRAFT',25,17),('Two independent Rd5.1k. USB optional data path is physically connected.',25,25),('USB contact-to-footprint mapping, CC/VBUS protection and inrush analysis remain open.',25,33),('SWD pogo pin numbering is project-specific; VTref is not a power input.',195,260)],
 'temperature': [('INDEPENDENT BATTERY NTC WINDOW - REVIEW DRAFT',25,17),('NTC103AT-2 /10k B3435 must be on CELL. No10k bypass resistor is permitted.',25,25),('Firmware P1.14 HIGH=inhibit viaQ2; LOW/HiZ permits hardware control.',25,33),('U8 holdsALLOWlow during reference startup. See tolerance calculation and tests.',25,281),('Pack acceptance: R0C>=24k, R45C<=5.20k, monotonic. Physical qualification required.',25,289)]
}

def library_symbol(s, name=None):
    n=s['name']; name=name or n
    w=s['width']/2; h=s['height']/2
    chunks=[f'(symbol {q(name)} (pin_names (offset 0.762)) (in_bom yes) (on_board yes)',prop('Reference','U',0,h+2.54),prop('Value',n,0,-h-2.54),prop('Footprint','',0,0,True),prop('Datasheet','',0,0,True)]
    if n=='C':
        shape='(polyline (pts (xy -2.54 0) (xy -0.508 0)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.508 0) (xy 2.54 0)) (stroke (width 0.254) (type default)) (fill (type none)))'
        shape+=' (polyline (pts (xy -0.508 -1.524) (xy -0.508 1.524)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.508 -1.524) (xy 0.508 1.524)) (stroke (width 0.254) (type default)) (fill (type none)))'
    else:
        shape=f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))'
    chunks.append(f'(symbol {q(n+"_0_1")} {shape})')
    pc=[]
    for p in s['pins']:
        pc.append(f'(pin {p["type"]} line (at {p["x"]} {p["y"]} {p["angle"]}) (length 2.54) (name {q(p["name"])} {effects(0.85)}) (number {q(p["num"])} {effects(0.85)}))')
    chunks.append(f'(symbol {q(n+"_1_1")} '+''.join(pc)+')')
    return '\n'.join(chunks)+')'

def placed(c,root_uuid):
    s=SYMS[c['symbol']]; x=c['x']; y=c['y']; ref=c['ref']
    h=s['height']/2
    out=[f'(symbol (lib_id {q("AnkleSensor:"+c["symbol"])}) (at {x} {y} 0) (unit 1) (in_bom '+('yes' if c['populate'] else 'no')+f') (on_board '+('no' if ref.startswith('#') else 'yes')+f') (dnp no) (uuid {q(c["uuid"])})',prop('Reference',ref,x,y-h-4.2),prop('Value',c['value'],x,y-h-1.8, size=0.9),prop('Footprint',c['footprint'],x,y,True),prop('Datasheet',c['datasheet'],x,y,True),prop('MPN',c['mpn'],x,y,True),prop('JLCPCB',c['jlcpcb'],x,y,True),prop('ReviewStatus',c['status'],x,y,True),prop('Note',c['note'],x,y,True)]
    for p in s['pins']:out.append(f'(pin {q(p["num"])} (uuid {q(uid(ref+"/pin/"+p["num"]))}))')
    out.append(f'(instances (project {q(PROJECT)} (path {q("/"+root_uuid+"/"+uid("sheet/"+c["sheet"]))} (reference {q(ref)}) (unit 1))))')
    return '\n'.join(out)+')'

def draw_sheet(name, root_uuid):
    cs=[c for c in COMPONENTS if c['sheet']==name]
    out=[f'(kicad_sch (version 20231120) (generator "ankle_sensor_review_generator") (uuid {q(uid("file/"+name))}) (paper "A3")',f'(title_block (title {q("Ankle Sensor V1 / "+name)}) (date "2026-10-28") (rev "A1-WIP") (comment 1 "WORK IN PROGRESS - SEE CURRENT ERC/DRC REPORTS"))','(lib_symbols']
    for sn in sorted(set(c['symbol'] for c in cs)):out.append(library_symbol(SYMS[sn], 'AnkleSensor:'+sn))
    out.append(')')
    for text,x,y in NOTES[name]:out.append(f'(text {q(text)} (at {x} {y} 0) {effects(1.05,"left")} (uuid {q(uid(name+text))}))')
    for c in cs:
        out.append(placed(c, root_uuid))
        for p in SYMS[c['symbol']]['pins']:
            net=c['pins'][p['num']]; x=round(c['x']+p['x'],5); y=round(c['y']-p['y'],5)
            key=c['ref']+'/'+p['num']
            if net is None:
                out.append(f'(no_connect (at {x} {y}) (uuid {q(uid(key+"/NC"))}))')
            else:
                ex=round(x+(-7.62 if p['side']=='left' else 7.62),5)
                out.append(f'(wire (pts (xy {x} {y}) (xy {ex} {y})) (stroke (width 0) (type default)) (uuid {q(uid(key+"/wire"))}))')
                out.append(f'(global_label {q(net)} (shape passive) (at {ex} {y} '+('0' if p['side']=='left' else '180')+f') {effects(0.9,"left")} (uuid {q(uid(key+"/label"))}) '+prop('Intersheetrefs','${INTERSHEET_REFS}',ex,y,True)+')')
    return '\n'.join(out)+')\n'

def main():
    HW.mkdir(exist_ok=True)
    project_path=HW/(PROJECT+'.kicad_pro')
    previous_project=json.loads(project_path.read_text()) if project_path.exists() else {}
    root_uuid=uid('root')
    root=[f'(kicad_sch (version 20231120) (generator "ankle_sensor_review_generator") (uuid {q(root_uuid)}) (paper "A3") (title_block (title "Ankle Sensor V1 - WORK IN PROGRESS") (date "2026-10-28") (rev "A1-WIP") (comment 1 "NOT FOR FABRICATION - SEE CHECK REPORTS")) (lib_symbols)']
    titles=['POWER PATH / BATTERY','MCU / RADIO / CLOCK','IMU / MEMORY','USB / CONTROLS / SWD','BATTERY TEMPERATURE']
    for idx, name in enumerate(NOTES):
        x=45+(idx%2)*125; y=55+(idx//2)*65; path=uid('sheet/'+name)
        root.append(f'(sheet (at {x} {y}) (size 80 30) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid {q(path)}) '+prop('Sheetname',titles[idx],x,y-2)+prop('Sheetfile',name+'.kicad_sch',x,y+32)+f'(instances (project {q(PROJECT)} (path {q("/"+root_uuid)} (page {q(idx+2)})))))')
        (HW/(name+'.kicad_sch')).write_text(draw_sheet(name,root_uuid))
    for idx, text in enumerate(['Electrical design in progress; see current PCB and check reports for completion status.','Review items: actual battery; clock loads; USB mechanical drawing and inrush.','KiCad10.0.7 is available. ERC/DRC status is recorded in reports, not inferred from this file.','Use README.md and docs/release_checklist.md before continuing design.']):
        root.append(f'(text {q(text)} (at 25 {25+idx*5} 0) {effects(1.05,"left")} (uuid {q(uid("rootnote"+str(idx)))}))')
    root.append(f'(sheet_instances (path "/" (page "1")))')
    (HW/(PROJECT+'.kicad_sch')).write_text('\n'.join(root)+')\n')
    (HW/'symbols'/'AnkleSensor.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "ankle_sensor_review_generator")\n'+'\n'.join(library_symbol(s) for s in SYMS.values())+')\n')
    (HW/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "AnkleSensor") (type "KiCad") (uri "${KIPRJMOD}/symbols/AnkleSensor.kicad_sym") (options "") (descr "Project symbols; independent library review required")))\n')
    previous_project.update({'meta':{'filename':PROJECT+'.kicad_pro','version':1}})
    previous_project.setdefault('net_settings',{'meta':{'version':3},'classes':[{'name':'Default','clearance':0.15,'track_width':0.2,'via_diameter':0.6,'via_drill':0.3,'microvia_diameter':0.3,'microvia_drill':0.1,'diff_pair_width':0.2,'diff_pair_gap':0.2,'diff_pair_via_gap':0.25}],'netclass_assignments':{},'netclass_patterns':[]})
    previous_project.setdefault('text_variables',{})['DESIGN_STATUS']='A1 WORK IN PROGRESS - NOT FOR FABRICATION'
    project_path.write_text(json.dumps(previous_project,indent=2)+'\n')
    (HW/'design.json').write_text(json.dumps({'status':'A1-WIP_NOT_FOR_FABRICATION','components':COMPONENTS,'open_nets':[],'test_nets':[],'notes':['Independent NTC window and128MiB selected; physical validation pending. See actual KiCad ERC/DRC reports.']},indent=2,ensure_ascii=False)+'\n')
    with (ROOT/'reports'/'bom_draft.csv').open('w',newline='') as f:
        fields=['ref','value','mpn','jlcpcb','footprint','status','note']
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        w.writerows(c for c in COMPONENTS if not c['ref'].startswith('#'))
    with (ROOT/'reports'/'pinmap.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Reference','PhysicalPin','PinName','Net'])
        for c in COMPONENTS:
            for p in SYMS[c['symbol']]['pins']:w.writerow([c['ref'],p['num'],p['name'],c['pins'][p['num']] or 'NC'])
    print(f'Generated {len(COMPONENTS)} symbols on {len(NOTES)} child sheets. This generator does not run ERC/DRC; see actual KiCad reports.')

if __name__=='__main__':main()
