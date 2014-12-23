#coding:utf-8

from pyMail import  ReceiveMailDealer
import sys
import os
import zipfile, rarfile

try:
    import debug
    usernm = debug.usernm
    passwd = debug.passwd
    server = debug.wangyi
    fpath = debug.fpath
except ImportError:
    usernm = passwd = qq = fpath = server = None

def unzip(fname):
    '''解压 zip 文件'''
    basename = os.path.basename(fname)
    zobj = zipfile.ZipFile(fname)
    print '###开始解压文件.......... %s'%basename
    for name in zobj.namelist():
        if not name.startswith('__MACOSX'):  #‘__MACOSX’为 mac 下压缩文件特有的
            f = open(os.path.join(os.path.dirname(fname), name), 'wb' )
            f.write(zobj.read(name))
            print '下载文件......%s成功'%name
            f.close()
    print '###解压完成'

def unrar(fname):
    '''解压 rar 文件'''
    basename = os.path.basename(fname)
    print '开始解压文件.......... %s'%basename
    robj = rarfile.RarFile(fname)
    for name in robj.namelist():
        name = str(name)
        if not name == basename[:-4]: 
            #rar 压缩文件会有一个等于文件名的0字节文件,需要忽略
            f = open(name[len(basename )+ 2:], 'wb')
            f.write(robj.read(name)) #TODO rarfile 库对于读取 doc/ppt 文件存在问题
            print '下载文件......%s成功'%name
            f.close()
    print '解压完成'

def download(data, filepath, filename, option=None):
    '''对压缩文件和非压缩文件进行下载. fpath:路径, fname:文件名'''
    if not option:
        print '文件类型不明确!!!!!'
        sys.exit(0)

    downloadfile = os.path.join(filepath, filename)
    if option == filetype.ZIP:
        #压缩文件
        
        #f = open(fpath + folder + '/' + fname, 'wb')
        f = open(downloadfile, 'wb')
        f.write(data) #暂存压缩文件
        f.close()

        unzip(downloadfile)
        os.remove(downloadfile) #删除暂存的压缩文件

    #elif option == filetype.RAR:
    #    f = open(downloadfile, 'wb')
    #    f.write(data) #暂存压缩文件
    #    f.close()
    #    unrar(downloadfile)
    #    os.remove(downloadfile) #删除暂存的压缩文件

    elif option == filetype.NORMAL:
        #非压缩文件
        f = open(downloadfile, 'wb')
        f.write(data)
        print '下载文件......%s成功'%filename
        f.close()

def zip_(path, zip_name):
    print '压缩文件夹 %s 里的所有文件'%folder
    f = zipfile.ZipFile(path +'/' + zip_name + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for _, _, filenames in os.walk(path):
        for filename in filenames:
            if not filename.startswith('.') and filename != (zip_name + '.zip'):
                f.write(path + '/' + filename)
    f.close()
    print '压缩完毕, 压缩文件：%s\n'%zip_name

class filetype():
    ZIP = 1
    NORMAL = 2
    RAR = 3

if __name__ == '__main__':

    folder = raw_input('输入新文件夹名(默认名为new_folder)')
    fpath = raw_input('输入新文件夹存放路径(默认当前目录)')
    if not folder:
        folder = 'new_folder'
    if not fpath:
        fpath = './'

    if os.path.exists(folder + '/'):
        print '文件夹%s已存在!!!!'%folder
        sys.exit(0)
    os.mkdir(folder)

    mailmanger = ReceiveMailDealer(usernm, passwd, server)

    t, nums = mailmanger.getUnread()
    nums = nums[0].split(' ')
    if nums == ['']:
        print '没有未读邮件'
        sys.exit(0)
    datas = {} #存放所有未读邮件的信息
    all_nums = [] #存放所有未读邮件的编号
    for num in nums:
        #加载所有未读邮件信息
        data = mailmanger.getMailInfo(num)
        datas.update({num : data})
        print '编号: %s  标题: %s  发件人: %s  附件个数: %d'%(num, datas[num]['subject'], datas[num]['from'][0], len(datas[num]['attachments']))
        all_nums.append(num)

    download_nums = raw_input('输入邮件编号(直接回车全选)')
    if not download_nums:
        download_nums = all_nums
    else:
        download_nums = download_nums.split(' ')
    if download_nums:
        print '\n你选择的邮件编号有： ', [num for num in download_nums]
        for num in download_nums:
            if num in nums:
                attachments = datas[num]['attachments'] #取到该邮件的所有附件
                for atta in attachments:
                    filename = atta['name']
                    data = atta['data']
                    filepath = os.path.join(fpath, folder)
                    if filename.endswith('.zip'):
                        #如果是压缩文件
                        download(data, filepath, filename, option=filetype.ZIP)
                    #elif fname.endswith('.rar'):
                    #    download(data, fpath, fname, option=filetype.RAR)
                    else:
                        #如果是普通文件
                        download(data, filepath, filename, option=filetype.NORMAL)
        print '所有邮件里的附件下载完成\n'
    else:
        print '输入为空，自动退出'
        sys.exit(0)

    zip_(fpath + folder, folder)
