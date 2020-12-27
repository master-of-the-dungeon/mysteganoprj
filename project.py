from PIL import Image, ImageOps
import wave, math, array, argparse, sys, timeit
from tkinter import Tk, Label

def createUI():
    root = Tk()
    lb = Label(root, text="Hello world", font="arial 32")
    lb.pack()
    root.mainloop()

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", help="Имя входного файла.")
    parser.add_argument("-n", "--name", help="Имя выходного файла.  Базовое имя: out.wav).")
    parser.add_argument("-b", "--bottom", help="Нижний порог частот. Базовое значение: 200.", type=int)
    parser.add_argument("-t", "--top", help="Верхний порог частот. Базовое значение: 20000.", type=int)
    parser.add_argument("-p", "--pixels", help="Пикселей в секунду. Базовое значение: 30.", type=int)
    parser.add_argument("-s", "--sampling", help="Частота дискретизации. Базовое значение: 44100.", type=int)
    args = parser.parse_args()

    minfreq = 200
    maxfreq = 20000
    wavrate = 44100
    pxs = 30
    name = "out.wav"

    if args.name:
        name = args.name
    if args.bottom:
        minfreq = args.bottom
    if args.top:
        maxfreq = args.top
    if args.pixels:
        pxs = args.pixels
    if args.sampling:
        wavrate = args.sampling


    print('Пеобразуемая картинка: %s.' % args.INPUT)
    print('Частотный диапазон: %d - %d.' % (minfreq, maxfreq))
    print('Пикселей в секунду: %d.' % pxs)
    print('Частота дискретизации: %d.' % wavrate)
    print('Имя выходного файла: %s.' % (args.name if name else 'out.wav'))

    return (args.INPUT, name, minfreq, maxfreq, pxs, wavrate)

def convert(inpt, name, minfreq, maxfreq, pxs, wavrate):
    img = Image.open(inpt).convert('L')
    name = wave.open(name, 'w')
    name.setparams((1, 2, wavrate, 0, 'NONE', 'not compressed'))

    freqrange = maxfreq - minfreq
    interval = freqrange / img.size[1]

    fpx = wavrate // pxs
    data = array.array('h')

    tm = timeit.default_timer()

    for x in range(img.size[0]):
        row = []
        for y in range(img.size[1]):
            yinv = img.size[1] - y - 1
            amp = img.getpixel((x,y))
            if (amp > 0):
                row.append( genwave(yinv * interval + minfreq, amp, fpx, wavrate) )

        for i in range(fpx):
            for j in row:
                try:
                    data[i + x * fpx] += j[i]
                except(IndexError):
                    data.insert(i + x * fpx, j[i])
                except(OverflowError):
                    if j[i] > 0:
                      data[i + x * fpx] = 32767
                    else:
                      data[i + x * fpx] = -32768

        sys.stdout.write("Преобразование в процессе, осталось: %d%%   \r" % (float(x) / img.size[0]*100) )
        sys.stdout.flush()

    name.writeframes(data.tostring())
    name.close()

    tms = timeit.default_timer()

    print("Преобразование в процессе, осталось: 100%")
    print("Успешно завершено за %d секунд." % int(tms-tm))

def genwave(frequency, amplitude, samples, samplerate):
    cycles = samples * frequency / samplerate
    a = []
    for i in range(samples):
        x = math.sin(float(cycles) * 2 * math.pi * i / float(samples)) * float(amplitude)
        a.append(int(math.floor(x)))
    return a

if __name__ == '__main__':
    #inpt = parser()
    #convert(*inpt)
    createUI()
