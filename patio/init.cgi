#! /usr/bin/perl

#��������������������������������������������������������������������
#�� Web Patio v3.4
#�� init.cgi - 2011/07/06
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������
$ver = '���肵�܎� Web Patio v3.4 k1.10';
# 2014/08/10 �X���b�h�̘A���쐬�A���X�̘A�����e�̏������[�`���̕ύX
# 2013/11/17 �{���̐F�Â��Ǝ��������N�̕s��̏C��
# 2013/03/03 �ߋ����O�̃o�O�C��
# 2012/09/08 �ߋ����O�ɗ��Ƃ��������C��
# 2011/07/06 3.4�ɍ��킹��
# 2011/04/27 3.31�ɍ��킹��
# 2010/11/14 �X���b�h�ԍ��̕\�����I�v�V�����őI�ׂ�悤��
# 2010/06/23 �V�K�X���b�h�쐬�ƃ��X�̃^�C�}�[�𕪂��Ă݂܂���
# 2009/07/31 �֎~���[�h�Ƀq�b�g�������e�����O�Ɏc���悤�ɂ��Ă݂܂���
# 2009/06/15 ���X�������������Ȃ�o�O�̏C��
# 2009/06/03 �^�C�g�����͎��ɖ{���𒼂��Ȃ�����I�v�V����������
# 2009/06/01 ���[�U�[�ԃ��[���@�\�𖳌��ɂł���悤��
# 2009/04/10 Google AdSense�̃R�[�h���I�v�V�����Ŗ������ł���悤�Ɂi�悭�Y���̂Łj
# 2009/04/07 �V�K�쐬���ɕ\�����J�X�^���ł���悤��
# 2009/03/18 FAQ���[�h�ɒ���
# 2009/03/14 �X���b�h�쐬�������[�h�̒ǉ�
# 2008/12/22 3.22�ɍ��킹��
# 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V
# 2008/01/15 ���X���m�点���[���̐ݒ��ǉ�
# 2007/12/17 �Ǘ��҂ɂ��ҏW���ɁA�p�X���[�h���������ǂ����I�v�V�����Ŏw��ł���悤�ɂ����B
# 2007/11/14 �ߋ����O��<->�����iadmin.cgi�̂ݕύX�j
# 2007/10/27 ���X�̑S���\��
# 2007/06/10 3.2�ɍ��킹��
# 2007/06/10 3.14�ɍ��킹��
# 2007/05/01 3.13�ɍ��킹��
# 2007/03/05 3.0�n�ɒ���
# �x�[�X�o�[�W����
# $ver = 'WebPatio v3.4';
#��������������������������������������������������������������������
#�� [���ӎ���]
#�� 1. ���̃X�N���v�g�̓t���[�\�t�g�ł��B���̃X�N���v�g���g�p����
#��    �����Ȃ鑹�Q�ɑ΂��č�҂͈�؂̐ӔC�𕉂��܂���B
#�� 2. �ݒu�Ɋւ��鎿��̓T�|�[�g�f���ɂ��肢�������܂��B
#��    ���ڃ��[���ɂ�鎿��͈�؂��󂯂������Ă���܂���B
#�� 3. �Y�t�摜�̂����A�ȉ��̃t�@�C�����Ĕz�z���Ă��܂��B
#��  �E�������ƃA�C�R���̕��� (http://www.ushikai.com/)
#��    alarm.gif book.gif fold4.gif glass.gif memo1.gif memo2.gif
#��    pen.gif trash.gif mente.gif
#��������������������������������������������������������������������
#
# �y�t�@�C���\����z
#
#  public_html (�z�[���f�B���N�g��)
#      |
#      +-- patio /
#            |    patio.cgi     [705]
#            |    read.cgi      [705]
#            |    regist.cgi    [705]
#            |    admin.cgi     [705]
#            |    registkey.cgi [705]
#            |    init.cgi      [604]
#            |    note.html
#            |    mail.log      [606] *���肵�܎��ŐV��
#            |    search.log    [606] *���肵�܎��ŐV��
#            |    setting.cgi   [705] *���肵�܎��ŐV��
#            |
#            +-- data / index1.log  [606]
#            |          index2.log  [606]
#            |          memdata.cgi [606]
#            |
#            +-- lib / jcode.pl     [604]
#            |         upload.pl    [604]
#            |         edit_log.pl  [604]
#            |         find.pl      [604]
#            |         check.pl     [604]
#            |         registkey.pl [604]
#            |
#            +-- log  [707] /
#            |
#            +-- ses  [707] /
#            |
#            +-- upl [707] /
#            |
#            +-- img / *.gif
#                      faq.gif            *���肵�܎��ŐV��
#                      filenew.gif        *���肵�܎��ŐV��
#                      fold6.gif          *���肵�܎��ō���
#                      foldnew.gif        *���肵�܎��ŐV��
#                      mail.gif           *���肵�܎��ŐV��

#�}�C�i�X�L�[���[�h��ݒ肷��
@keyword = ('�L�[���[�h1 �L�[���[�h2');

#�O���̐ݒ�
$d = 30;

use Time::Local;
use File::Basename qw/basename dirname/;
use File::Spec;
use Encode qw//;
use Symbol qw//;

#===========================================================
#  ����{�ݒ�
#===========================================================

# �O���t�@�C��
$jcode   = './lib/jcode.pl';
$upload  = './lib/upload.pl';
$editlog = './lib/edit_log.pl';
$findpl  = './lib/find.pl';
$checkpl = './lib/check.pl';
$regkeypl = './lib/registkey.pl';

# �������݋֎~���[�h (0=�ʏ퓮�� 1=�������݋֎~)
$ReadOnly =0;

# �������݋֎~���[�h���ɕ\�����邨�m�点
$Oshirase = '�����e�i���X���ɂ��A�������݋֎~���[�h�œ��삵�Ă��܂��B';

# �Ǘ��p�X���[�h�i�p������8�����ȓ��j
$pass = 'pass';

# �X���b�h���O�̉{���A�ۑ� Cookie ID
@thread_Edit = ( '01_hoge', '01_hoge2');

#�S���X�\��/�r�����X�Ԃ̕\��
$middle_number = 50;
# �A�N�Z�X����������
# 0=no 1=yes
$authkey = 0;

# ���O�C���L�����ԁi���j
$authtime = 60;

# �摜�A�b�v��������i�e�L���̂݁j
# 0=no 1=yes
$image_upl = 1;

# �g���b�v�@�\�i�n���h���U���h�~�j�̂��߂̕ϊ��L�[
# ���@�p������2����
$trip_key = 'ab';

# �^�C�g��
$title = '���肵�܎� Web Patio ������';

# �f���̐���
$desc = '�����R�ɏ������݉�����';

# �^�C�g���̕����F
$t_color = "#000000";

# �^�C�g���T�C�Y
$t_size = '18px';

# �{�������T�C�Y
$b_size = '13px';

# �{�������t�H���g
$b_face = '"MS UI Gothic", Osaka, "�l�r �o�S�V�b�N"';

# ���[���{���p�{��CGI��URL�iread.cgi�܂ł̃t���p�X�j
$fullscript = 'http://freeden.e7.valueserver.jp/webpatio/patio/read.cgi';

# �f���{��CGI�yURL�p�X�z
$bbscgi = './patio.cgi';

# �f�����eCGI�yURL�p�X�z
$registcgi = './regist.cgi';

# �f���{��CGI�yURL�p�X�z
$readcgi = './read.cgi';

# �X���b�h�\��Ajax�ʐM�pAPI CGI�yURL�p�X�z
$readapicgi = './read_api.cgi';

# �f���Ǘ�CGI�yURL�p�X�z
$admincgi = './admin.cgi';

# ���ӎ����y�[�W�yURL�p�X�z
$notepage = './note.html';

# ���s���Oindex�y�T�[�o�p�X�z
$nowfile = './data/index1.log';

# �ߋ����Oindex�y�T�[�o�p�X�z
$pastfile = './data/index2.log';

# ����t�@�C���y�T�[�o�p�X�z
$memfile = './data/memdata.cgi';

# �L�^�t�@�C���f�B���N�g���y�T�[�o�p�X�z
$logdir = './log';

# �Z�b�V�����f�B���N�g���y�T�[�o�p�X�z
$sesdir = './ses';

# �߂��yURL�p�X�z
$home = './patio.cgi';

# �ǎ�
$bg = "";

# �w�i�F
$bc = "#F0F0F0";

# �����F
$tx = "#000000";

# �����N�F
$lk = "#0000FF";
$vl = "#800080";
$al = "#DD0000";

# �摜�f�B���N�g���yURL�p�X�z
$imgurl = './img';

# �L���̍X�V�� method=POST ���� (0=no 1=yes)
# �i�Z�L�����e�B�΍�j
$postonly = 1;

# �A�����e�̋֎~���ԁi�b�j���g�p���Ă��܂���B����2�Ŏw�肵�ĉ������B
# $wait = 60;

# �X���b�h�쐬�Ԋu�i�b�j�i���肵�܎��ŐV�݁j
$wait_thread = 0;

# ���X���e�Ԋu�i�b�j
$wait_response_default = 0;
$wait_response1 = 0;
$wait_response2 = 0;
$wait_response3 = 0;

# �X���b�h�^�C�g���ɂ�铊�e�Ԋu�̕ύX(���X)
# (���L�̂�����ɂ����v���Ȃ��ꍇ�́A$wait_response_default ����� $responselog_default ���g�p���܂�)
$wait_response_word1 = ''; # �X���b�h�^�C�g���Y�����A$wait_response1 ����� $responselog1 ���g�p���܂�
$wait_response_word2 = ''; # �X���b�h�^�C�g���Y�����A$wait_response2 ����� $responselog2 ���g�p���܂�
$wait_response_word3 = ''; # �X���b�h�^�C�g���Y�����A$wait_response3 ����� $responselog3 ���g�p���܂�

# �V�K���e�̋L�^�t�@�C���i���肵�܎��ŐV�݁j
$threadlog = './thread.log';

# �ԐM�̋L�^�t�@�C��
$responselog_default = './response_default.log';
$responselog1 = './response1.log';
$responselog2 = './response2.log';
$responselog3 = './response3.log';

# $threadlog �� $responselog �ɋL�^����z�X�g���i���肵�܎��ŐV�݁j
# �������݋֎~���Ԃ��߂���ƃf�[�^�͔j�������̂ŁA���܂�傫�Ȑ���ݒ肵�Ă������܂ŋL�^����Ȃ��͂�
$hostnum = 10;

# ���t�ʃX���b�h�쐬�����O�t�@�C��
$thread_create_countlog = './thread_create_count.log';

# ���t�ʃ��X�������ݐ����O�t�@�C��
$response_countlog = './response_count.log';

# �X���b�h�����p�ŏI�X�V�����L�^SQLite�t�@�C��
$thread_updatelog_sqlite = './db/thread_updatelog.sqlite';

# �������Ԏw��̏����l�w��
$d = 30;

# �֎~���[�h
# �� ���e���֎~���郏�[�h���R���}�ŋ�؂�@�ȉ��͂��肵�܎��̃T���v���f���Őݒ肵���֎~���[�h�̈ꗗ
#�@�@�K�v�ɉ����čs���� # ���폜���ėL���ɂ��Ă��������B
#    �Q�ڈȍ~�̃��X�g�́u,�v�ŋ�؂��Ă���n�߂邱�ƁB
#   �i�P�ڂ̃��X�g�j$no_wd = '�A�_���g,�o�,�J�b�v��';
#   �i�Q�ڈȍ~�̃��X�g�j$no_wd = $no_wd.',�A�_���g,�o�,�J�b�v��';
#    ���f�������݂ɑ����uhttp�v���w�肷��Ƃ��Ȃ���ʂ�����Ǝv���܂�
#    �s���I�h�u.�v���g���ƌ딻��̌��Ȃ̂Œ���
# $no_wd = '';

# �֎~��̋L�^�t�@�C���i���肵�܎��ŐV�݁j
$badwordlog = './badword.log';

#TODO 2017/10/26
#���O�����������p�i�g���b�v�܂܂Ȃ�
$name_length_no_trip = 10;
#���O�����������p�i�g���b�v�܂�
$name_length_trip = 5;
#�X���b�h�^�C�g�������������p
$sub_length = 10;
#TODO 2017/10/27

# �X���b�h�^�C�g�����ݒ�l�ɒ��Ԉ�v�ō��v����X���b�h�́ARSS�ipatio.cgi?mode=feed�̈ꗗ�j�ɏo�͂��܂���B
@rss_no_word=('�e�X�g','kate2','�A���J�[','�X�}�z');

#�@�@�u���b�N���O��蒊�o�������ʂ̂������L�[���[�h
$no_wd = '����,�X�[�p�[�R�s�[';

# �t���[Web�n�֎~���[�h �����[�U�[�̈��ӂ̂Ȃ��y�[�W���͂������\��������܂�
#                         ���W���[�n�łȂ��t���[Web�̏ꍇ�́AURL�n�֎~���[�h�Ɋ܂܂�Ă��邩������܂���
# $no_wd = $no_wd.',tripod,usearea';

# ���O��NG���[�h�@�\(�֎~������`�F�b�N)
# ���O���œ��͂��֎~���镶����𔼊p�J���}��؂�Ŏw�肵�܂�
$ng_nm = "";

# ���O��NG���[�h�@�\(���͋������`�F�b�N)
# ���O���œ��͂������镶����Unicode�����R�[�h���K�\���Ŏw�肵�܂�
# ���K�\���͕K���_�u���N�I�[�e�[�V�����ň͂�Ŏw�肵�ĉ�����
# �ق��A�g���b�v�쐬���ʎq�u#�v�́A�v���O�������Œǉ����Ă��܂�
#
# �܂��A1���w�肵�Ȃ��ꍇ(@permit_name_regex = ();)��
# ���͋������̃`�F�b�N���s���܂���
# =====================================================
# Unicode �����R�[�h���K�\����
# =====================================================
# ���p����: \N{U+0030}-\N{U+0039}
# �S�p����: \N{U+FF10}-\N{U+FF19}
# ���p�p��: \N{U+0041}-\N{U+005A}\N{U+0061}-\N{U+007A}
# �S�p�p��: \N{U+FF21}-\N{U+FF3A}\N{U+FF41}-\N{U+FF5A}
# �Ђ炪��: \N{U+3041}-\N{U+3096}
# ���p�J�^�J�i: \N{U+FF66}-\N{U+FF6F}\N{U+FF71}-\N{U+FF9D}
# �S�p�J�^�J�i: \N{U+30A1}-\N{U+30FA}
# ����: \\p{Han}
# �����p���_�E�����_: \N{U+3099}\N{U+309A}
# ���p�Ɨ����_�E�����_(�J����сK): \N{U+FF9E}\N{U+FF9F}
# �S�p�Ɨ����_�E�����_(�J����сK): \N{U+309B}\N{U+309C}
# ���p�X�y�[�X( ): \N{U+0020}
# �S�p�X�y�[�X(�@): \N{U+3000}
# ���p���Q��(!): \N{U+0021}
# �S�p���Q��(�I): \N{U+FF01}
# ���p��Ǔ_(�A����сB): \N{U+FF64}\N{U+FF61}
# �S�p��Ǔ_(�A����сB): \N{U+3001}\N{U+3002}
# ���p���_(�E): \N{U+FF65}
# �S�p���_(�E): \N{U+30FB}
# ���p����(�[): \N{U+FF70}
# �S�p����(�[): \N{U+30FC}
# �n�C�t���}�C�i�X(-): \\\N{U+002D}
# ���p�v���X(+): \N{U+002B}
# �S�p�v���X(�{): \N{U+FF0B}
# ���p�s���I�h(.): \N{U+002E}
# �S�p�s���I�h(�D): \N{U+FF0E}
# ���p����(=): \N{U+003D}
# �S�p����(��): \N{U+FF1D}
# ���p(#): \N{U+0023}
# �S�p(#): \N{U+FF03}
# (��): \N{U+25C6}
# =====================================================
@permit_name_regex = (
                      "\N{U+0030}-\N{U+0039}", # ���p����
                      "\N{U+FF10}-\N{U+FF19}", # �S�p����
                      "\N{U+0041}-\N{U+005A}\N{U+0061}-\N{U+007A}", # ���p�p��
                      "\N{U+FF21}-\N{U+FF3A}\N{U+FF41}-\N{U+FF5A}", # �S�p�p��
                      "\N{U+3041}-\N{U+3096}", # �Ђ炪��
                      "\N{U+FF66}-\N{U+FF6F}\N{U+FF71}-\N{U+FF9D}", # ���p�J�^�J�i
                      "\N{U+30A1}-\N{U+30FA}", # �S�p�J�^�J�i
                      "\\p{Han}", # ����
                      "\N{U+3099}\N{U+309A}", # �����p���_�E�����_
                      "\N{U+FF9E}\N{U+FF9F}", # ���p�Ɨ����_�E�����_
                      "\N{U+309B}\N{U+309C}", # �S�p�Ɨ����_�E�����_
                      "\N{U+0020}", # ���p�X�y�[�X
                      "\N{U+3000}", # �S�p�X�y�[�X
                      "\N{U+0021}", # ���p���Q��
                      "\N{U+FF01}", # �S�p���Q��
                      "\N{U+FF64}\N{U+FF61}", # ���p��Ǔ_
                      "\N{U+3001}\N{U+3002}", # �S�p��Ǔ_
                      "\N{U+FF65}", # ���p���_
                      "\N{U+30FB}", # �S�p���_
                      "\N{U+FF70}", # ���p����
                      "\N{U+30FC}", # �S�p����
                      "\\\N{U+002D}", # �n�C�t���}�C�i�X
                      "\N{U+002B}", # ���p�v���X
                      "\N{U+FF0B}", # �S�p�v���X
                      "\N{U+002E}", # ���p�s���I�h
                      "\N{U+FF0E}", # �S�p�s���I�h
                      "\N{U+003D}", # ���p����
                      "\N{U+FF1D}", # �S�p����
                      "\N{U+0023}", # ���p(#)
                      "\N{U+FF03}", # �S�p(#)
                      "\N{U+25C6}", # (��)
                      );

# ���{��`�F�b�N�i���e�����{�ꂪ�܂܂�Ă��Ȃ���΋��ۂ���j
# 0=No  1=Yes
$jp_wd = 1;

# URL���`�F�b�N
# �� ���e�R�����g���Ɋ܂܂��URL���̍ő�l
$urlnum = 1;

# ���O���͕K�{ (0=no 1=yes)
$in_name = 0;

# E-Mail���͕K�{ (0=no 1=yes)
# E-Mail���͕K�{ (0=no 1=yes 2=���͗���\���E���͋֎~ 3=���͋֎~)
# ������2��3�ɂ���ƃ��X���m�点���[���@�\�����p�ł��܂���B
$in_mail = 1;

# E-Mail�\�� (0=��\�� 1=�\��) ��������\���ɂ��Ă��A���[�U�[�����[���A�h���X��\����I�Ԃƕ\������܂���
# �X�p���h�~�̂��߁A�ύX���Ȃ����Ƃ𐄏��B
$show_mail = 0;

# URL���̓��͔���
# ���f�������ݖh�~�p (0=�Ȃɂ����Ȃ� 1=�K�{ 2=���͗���\���E���͋֎~ 3=���͋֎~)
# 2��3�̏ꍇ�͋L�����ɂ��\������܂���B
$in_url = 2;

# �폜�L�[���͕K�{ (0=no 1=yes)
$in_pwd = 0;

# 1�̃X���b�h���O�t�H���_���̃X���b�h���O�t�@�C���ۑ���
# �X���b�h���O�t�@�C���𕡐��̃t�H���_�ɕ����ۑ�����ۂ�
# 1�̃t�H���_���ɕۑ�����X���b�h���O�t�@�C������ݒ肵�܂�
# 0�ȉ��̐���ݒ肷��ꍇ�A$logdir�����ɑS�ẴX���b�h���O��ۑ����܂�
# (�ݒ�ύX�����ۂ́A�Ǘ���ʂ���ۑ��t�H���_�Ĕz�u�������s���ĉ�����)
$number_in_threadlog_folder = 50000;

# ���s���O�ő�X���b�h��
# �� ����𒴂���Ɖߋ����O�ֈړ�
$i_max = 1000;

# �ߋ����O�ő�X���b�h��
# �� ����𒴂���Ǝ����폜
$p_max = 3000;

# 1�X���b�h����́u�\���v�L����
$t_max = 100;

# 1�X���b�h����́u�ő�v�L����
# �� ����𒴂���Ɖߋ����O�։��܂�
# �� �c��90%�ŃA���[����\�����܂�
$m_max = 1000;

# ���s���O�������j���[�̃X���b�h�\����
$menu1 = 20;

# �ߋ����O�������j���[�̃X���b�h�\����
$menu2 = 20;

# �F�w��i���ɁA�Z�F�A���F�A���ԐF�j
$col1 = "#8080C0";
$col2 = "#FFFFFF";
$col3 = "#DCDCED";

# �J�z�y�[�W���̓��Y�y�[�W�̐F
$pglog_col = "#DD0000";

# �R�����g���͕������i�S�p���Z�j
$max_msg = 5000;

# JPG, PNG�摜1��������̍ő哊�e�T�C�Y (bytes)
# �� �� : 102400 = 100KB
# 2MB=2048000
$maxdata = 5350000;

# GIF�摜1��������̍ő哊�e�T�C�Y (bytes)
$maxdata_gif = 15350000;

# �X�}�C���A�C�R���̎g�p (0=no 1=yes)
$smile = 1;

# �X�}�C���A�C�R���̒�` (�X�y�[�X�ŋ�؂�)
# �� �������A���̐ݒ�ӏ��͕ύX���Ȃ��ق�������
# �� �當���ɔ��p�J�i��2�o�C�g�����͎g�p���ցi���K�\����̐���j
$smile1 = 'smile01.gif smile02.gif smile03.gif smile04.gif smile05.gif smile06.gif smile07.gif';
$smile2 = '(^^) (^_^) (+_+) (^o^) (^^;) (^_-) (;_;)';

# ���[�����M
# 0 : ���Ȃ�
# 1 : �X���b�h������
# 2 : ���e�L�����ׂ�
$mailing = 0;

# ���[�����M��
$mailto = '';

# ���[�����M���̍��o�l
# �� : ���[���A�h���X�̓��͂�����΂��̃A�h���X
# ���[���A�h���X���w�� : �˂Ɏw�肵�����[���A�h���X���瑗�M
$sender = '';

# ���[�����M��i�a�b�b�j
$bccto = '';

# sendmail�p�X
# �ʏ�͂���
$sendmail = '/usr/sbin/sendmail';
# ������C���^�[�l�b�g�͂�����
# $sendmail = '/usr/sbin/sendmail';

# �z�X�g�擾���@
# 0 : gethostbyaddr�֐����g��Ȃ�
# 1 : gethostbyaddr�֐����g��
$gethostbyaddr = 1;

# �A�N�Z�X�����i���p�X�y�[�X�ŋ�؂�A�A�X�^���X�N�j
#  �� ���ۃz�X�g�����L�q�i�����v�j�y��z*.anonymizer.com
$deny_host = '';

#  �� ����IP�A�h���X���L�q�i�O����v�j�y��z210.12.345.*
$deny_addr = '';

# VPNGate�o�R�ł̏������݂�����
# 0 : ���ۂ��Ȃ�
# 1 : ���ۂ���(�������ݎ��ɃG���[���b�Z�[�W��\�����܂�)
$deny_post_via_vpngate = 1;

# �摜�����ۑ� �t�H���_�ԍ����O�t�@�C��
# �摜�t�@�C���𕪊��ۑ�����ۂ�
# �t�H���_�ԍ����L�^���郍�O�t�@�C���p�X��ݒ肵�܂�
$img_folder_number_log = './img_folder_number.log';

# �摜�����ۑ� �t�H���_���摜�����O�t�@�C��
# �摜�ۑ��t�H���_���̉摜�t�@�C�������L�^����
# ���O�t�@�C���p�X��ݒ肵�܂�
$imgfile_count_log = './imgfile_count.log';

# �摜�����ۑ� �t�H���_���摜�ۑ������
# �摜�t�@�C���𕪊��ۑ�����ۂ�
# 1�̃t�H���_���ɕۑ�����摜�t�@�C���̏������ݒ肵�܂�
$max_number_of_imgfiles_in_folder = 10000;

# �摜�f�B���N�g���i�摜�A�b�v��������Ƃ��j
# �� ���ɁA�T�[�o�p�X�AURL�p�X
$upldir = './upl';
$uplurl = './upl';

# �ő�ŉ摜6���̃A�b�v���[�h
# �A�b�v���[�h�\���� �������ݒ� (0�`3��)
$upl_increase_num = 3;

# �A�b�v�摜�̕\�������Ӎő�T�C�Y�i�P�ʁF�s�N�Z���j
# �� �T���l�C���摜�@�\�L�����́A���̃T�C�Y�ŃT���l�C���摜��\�����܂�
$img_max_w = 200;	# ����
$img_max_h = 200;	# �c��

# �A�b�v�摜���ϊ��t�@�C���T�C�Y���(�P��:�o�C�g)
# �A�b�v�摜��"�ϊ����Ȃ�"�t�@�C���T�C�Y����l��ݒ肵�܂�
# �� ���̐ݒ�l�����傫���t�@�C���T�C�Y��jpg/png�t�@�C�����A�b�v���[�h���ꂽ�ۂ�
#   �A�b�v�摜�̕ϊ����s���܂�
$img_no_convert_filesize_max = 0;

# �A�b�v�摜�ϊ���JPEG���k�i���ݒ�
# �A�b�v�摜�̕ϊ����s���ۂ�JPEG���k�i����ݒ肵�܂�
# 1�`100�̊Ԃ̐����Ŏw�肵�ĉ�����
$img_jpeg_compression_level = 80;

# �A�b�v�摜�ϊ����ő剡��(�P��:�s�N�Z��)
# �A�b�v�摜�̕ϊ����s���ۂ̍ő剡����ݒ肵�܂�
# �� �ϊ����ɃA�b�v�摜���������̐ݒ�l���傫���ꍇ��
#   ���̐ݒ�l�̉����܂ŃA�X�y�N�g���ۂ��ďk������܂�
$img_convert_resize_w = 1600;

# �A�b�v����PNG�摜�ϊ��� �A���t�@�`�����l�������F�ݒ�
# ����PNG��JPEG�ɕϊ�����ۂ̃A���t�@�`�����l���Ƃ̍����F��ݒ肵�܂�
# #rrggbb �`���Ŏw�肵�ĉ�����
$img_alphachannel_composite_color = '#ffffff';

# �T���l�C���摜���쐬����i�v�FImage::Magick�j
# �� �k���摜�������������A�摜�L���̕\�����x���y������@�\
# 0=no 1=yes
$thumbnail = 1;

# �T���l�C���摜�̐��������Ӎő�T�C�Y�i�P�ʁF�s�N�Z���j
$thumb_max_w = 200;	# ����
$thumb_max_h = 200;	# �c��

# �T���l�C���摜JPEG���k�i���ݒ�
# �T���l�C���摜��������JPEG���k�i����ݒ肵�܂�
# 1�`100�̊Ԃ̐����Ŏw�肵�ĉ�����
$thumb_jpeg_compression_level = 80;

# �T���l�C���摜 �A�j���[�V����GIF �����摜�p�X
# �A�j���[�V����GIF�̃T���l�C���摜�ɍ�������摜�p�X��ݒ肵�܂�
$thumb_composite_img_path = './lib/play.gif';

# �T���l�C���摜 �A�j���[�V����GIF �����摜 �s�����x
# �A�j���[�V����GIF�̃T���l�C���摜�ɍ�������摜�̕s�����x��ݒ肵�܂�
# 0�`100�̐����Ŏw�肵�ĉ�����
$thumb_composite_img_opacity = 70;

# �T���l�C���摜�ۑ���f�B���N�g��(�f�B���N�g���̃p�[�~�b�V������777�ł���K�v������܂�)
# �� ���ɁA�T�[�o�p�X�AURL�p�X
$thumbdir = './thumb';
$thumburl = './thumb';

#�摜�̃e�L�X�g�����N��PhotoSwipe�Ή��� �����N�C��
$domain_pc_name = 'http://hogehoge.com/patio/';

# �A�b�v�摜�t�@�C�����\���̐擪�ɒǉ����镶����
# (�{���������ɂ��g�p�@��E����������ʂ��܂�)
$img_filename_prefix = 'upl/';

## --- <�ȉ��́u���e�L�[�v�@�\�i�X�p���΍�j���g�p����ꍇ�̐ݒ�ł�> --- ##
#
# �V�K�X���b�h�쐬�t�H�[���ł̓��e�L�[�̎g�p
# �� 0=no 1=yes
$regist_key_new = 0;

# �X���b�h���ԐM�t�H�[��/���[�U�[�ԃ��[�����M�t�H�[���ł̓��e�L�[�̎g�p
# �� 0=no 1=yes
$regist_key_res = 0;

# ���e�L�[�摜�����t�@�C���yURL�p�X�z
$registkeycgi = './registkey.cgi';

# ���e�L�[�Í��p�p�X���[�h�i�p�����łW�����j
$pcp_passwd = 'patio123';

# ���e�L�[���e���ԁi���P�ʁj
#   ���e�t�H�[����\�������Ă���A���ۂɑ��M�{�^�����������
#   �܂ł̉\���Ԃ𕪒P�ʂŎw��
$pcp_time = 30;

# ���e�L�[�摜�̑傫���i10�| or 12�|�j
# 10pt �� 10
# 12pt �� 12
$regkey_pt = 10;

# ���e�L�[�摜�̕����F
# �� $text�ƍ��킹��ƈ�a�����Ȃ��B�ڗ�������ꍇ�� #dd0000 �ȂǁB
$moji_col = '#dd0000';

# ���e�L�[�摜�̔w�i�F
# �� $bc�ƍ��킹��ƈ�a�����Ȃ�
$back_col = '#F0F0F0';

#-------------------------------------------------
#  ������ȉ��� ���肵�܎� �̐ݒ荀�ڂł��B
#-------------------------------------------------

# �V���\������
# �P�ʁF�b
# $hot = 43200; # 12����
# $hot = 72000; # 20����
$hot = 259200; # 72����

# NEW�̕\�����e�iHTML�j
$newmark = " <font color=#FF0000><b>NEW</b></font>";
# $newicon = ""; �u�����N�ɂ���Ζ����Ɠ���

# �V���̂���X���b�h�̃A�C�R��
#$newfold = "foldnew.gif";

# �V�����X�̃A�C�R��
#$newfile = "filenew.gif";

# �F�w��E���ӐF
$col4 = "#FF0000";

# ���ӐF�̔w�i�F
$col5 = "#FF9999";

# ���e��ʂ̃R�����g���̍s��
$rows = 15;

# ���e��ʂ̃R�����g���̌���
$cols = 72;

# �V�K�X���b�h�쐬���̃R�����g���̍s��
$newrows = 20;

# ���X�̃f�t�H���g�^�C�g���̐ݒ�^�薼��w��i�v���r���[�j
$restitle = 1;
# 0 : ��
# 1 : �uRe: ���̃^�C�g���v���v���r���[����
# ���肵�܎��̓X���b�h�ꗗ�Ƀ��X�̃^�C�g��������̂� 0 : �� ����������
# 1 �ɂ����ꍇ�͓����Ƀv���r���[�������ɂȂ�܂��B

# �X���b�h�̔ԍ��\��
$showthreadno = 1;
# 0 : �\�����Ȃ�
# 1 : [�X���b�h�ԍ�]��\������

# �����N�̍ۂ̃^�[�Q�b�g
$target="_blank";
# �L�����̃����N���N���b�N���邽�тɐV�����E�C���h�E���J�������Ȃ��ꍇ��
# $target="_top"; # �Ȃǂ�K���ɐݒ�

# ���p�����̐F >
$quotecol="#6495ED";

# ���p�����̐F(2) *
$quotecol2="#FF6600";

# ���p�����̐F(3) #
$quotecol3="#AAAAAA";

# ID�@�\�̗��p
# 0 : ID�@�\�𗘗p���Ȃ�
# 1 : ID�@�\�𗘗p����
$idkey = 1;

# �^�C�g���̕�����
$sublength = 80;

# ���[���̑��MIP�L�^�t�@�C��
$mailfile = './mail.log';

# ���[�����M�\�Ԋu�i�b�j
$mailwait = 60;

# ���X���������Ƃ��ɂ��m�点 0=���Ȃ� 1=�X�����Ă��l�̂� 2=�R�����g�����l���܂ߑS��
$mailnotify = 0;

# ���m�点�̑��M���Ƃ��Ďg�p����A�h���X
$notifyaddr = '';

# ���m�点�̔z�M�����ۂ��Ă���A�h���X�i,�ŋ�؂��ĕ����w��j
# ���̕�����Ƀ}�b�`�����ꍇ�͔z�M����܂���i������Ȃ̂Œ��Ӂj�j
$refuseaddr = '';

# ������̋L�^�t�@�C��
$srchlog = './search.csv';

# �Ǘ��l���L����ҏW�����ꍇ�A�������݂������{�l���ҏW�ł��Ȃ��悤�Ƀp�X���[�h���N���A����
# 0 : �p�X���[�h���ێ�����
# 1 : �p�X���[�h���N���A����i�{�l�ҏW�s�j
$clearpass = 1;

# �X���b�h�쐬�ɂ́A�Ǘ��p�X���[�h�̓��͂�K�{�ɂ���
# �L���ɂ���ƁA�����I�ɊǗ��҂����X���b�h�𗧂Ă邱�Ƃ��ł��Ȃ��Ȃ�܂��B
# 0 : �����ɂ���
# 1 : �Ǘ��p�X���[�h�̓��͂�K�{�ɂ���
$createonlyadmin = 0;

# �X���b�h�쐬���̒��ӏ����i�R�����g���̑O�ɕ\������܂��j
$createnotice = "";

# �X���b�h�쐬���̃e���v���[�g�i�R�����g���ɏ����\������܂��j
$createtemplate ="�e���v���[�g�W�J\n\\n���g�p���邱�Ƃ�\n�����s���Ή�";

# Google AdSense�̃R�[�h��\�������郋�[�`����L���ɂ��邩�ݒ肵�܂��B
# �R�[�h�� init.cgi �̖����� sub googleadsense ���ɋL�q���܂��B
# 0 : �����ɂ���
# 1 : �L���ɂ���
$adsenseenable = 0;

# ���[�U�[�Ԃ̃��[�����M�@�\
# ���[���A�h���X����͂������[�U�[�����[���A�h���X���\���Ń��[�����󂯎��@�\
# �v���o�C�_�[�ɂ���Ă̓Z�L�����e�B�㓮�삵�Ȃ��ꍇ�͖����ɂ��Ă��������B
# 0 : �����ɂ���
# 1 : �L���ɂ���
$usermail = 1;

# �v���r���[���Ɋ����͕���ҏW�ł��邩
# ('disabled'=�߂��ĕҏW ''=���̂܂ܕҏW�\)
# 0=�� 1=�s��
$editpreview ='1';

# �֎~��̋L�^�t�@�C��
$badwordlog = './badword.log';

#-------------------------------------------------
#  ���擾����UserAgent�̕ύX�@�\ �ݒ荀��
#-------------------------------------------------

# UserAgent����u,�v�Ɓu:�v����菜���A�u_�v���u-�v�ɒu�������A
# ���̌�A���̐ݒ�l�Ŏw�肳�ꂽ���������菜���܂�
# �ݒ�l�́u,�v��؂�Ŏw�肵�܂�
@useragent_remove_strings = (
);

#-------------------------------------------------
#  ��NG���X(NGID/NG�l�[��)�@�\ �ݒ荀��
#-------------------------------------------------

# NGID/NG�l�[���Ƃ��ēo�^���ꂽ���[�U�[�̃R�����g��u�������郁�b�Z�[�W
# (���b�Z�[�W��HTML���g�p���邱�Ƃ��ł��܂�)
$ngres_comment = "";

# NGID�@�\�̗��p
# ID�@�\���L���ɂȂ��Ă���Ƃ�($idkey = 1;)�̂ݗ��p�ł��܂�
# 0 : NGID�@�\�𗘗p���Ȃ�
# 1 : NGID�@�\�𗘗p����
$ngid = 1;

# NGID�̓o�^����ɒB������A����ɓo�^���悤�Ƃ������̃G���[���b�Z�[�W
$ngid_error_message = "NGID�o�^���̏���ɒB���Ă��܂��B";

# NG�l�[���@�\�̗��p
# 0 : NG�l�[���@�\�𗘗p���Ȃ�
# 1 : NG�l�[���@�\�𗘗p����
$ngname = 1;

# NG�l�[���̓o�^����ɒB������A����ɓo�^���悤�Ƃ������̃G���[���b�Z�[�W
$ngname_error_message = "NG�l�[���o�^���̏���ɒB���Ă��܂��B";

# NG�l�[���K�p���X���O���J�b�g�\���@�\ �Œ�\��������
# ���̕������𒴂��閼�O���̕����ɂ��āANG�l�[���K�p���X�̎��ɕ\�����B����܂�
# -1�Ȃ�0�����̒l��ݒ肷��ƁANG�l�[���K�p���X�ł����O����S�ĕ\�����܂�
$ngname_dispchar_length = 3;

# NG���X�� ��Q�ƃ��X���� ��\���@�\
# ��Q�ƃ��X�����\���un���̃��X�v���\������Ă��郌�X��NG���X�̎��ɁA
# ��Q�ƃ��X�����\�����\���ɂ��܂�
# (��\���ɂ��邩�ǂ����̐ݒ�ŁA�ʏ�Ǝw�肪�t�ɂȂ�܂��̂ł����Ӊ�����)
# 0 : NG���X���ɂ���Q�ƃ��X������\�����܂�
# 1 : NG���X���ɂ͔�Q�ƃ��X������\�����܂���
$ngres_hide_refcounter = 1;

# �A��NG�@�\ �f�t�H���g�l�ݒ�
# �A��NG�@�\�̗L��/���������[�U�[�ɂ���Đݒ肳��Ă��Ȃ�����
# �f�t�H���g�l��ݒ肵�܂�
# 0 : �A��NG�@�\�𖳌��ɂ���
# 1 : �A��NG�@�\��L���ɂ���
$chain_ng = 1;

#-------------------------------------------------
# ����Q�ƃ��X�����\���E�W�J�\���@�\ �ݒ荀��
#-------------------------------------------------

# ��Q�ƃ��X�����J�E���g ��Ώۃ��X �A���J�[���ݒ�
# �ݒ萔�ȏ�̃A���J�[���܂ރ��X�́A�J�E���g�ΏۂɂȂ�܂���
$number_of_anchor_made_ref_count_exempt = 6;

#-------------------------------------------------
#  ��NG�X���b�h�@�\ �ݒ荀��
#-------------------------------------------------

# NG�X���b�h�\�� �f�t�H���g�l�ݒ�
# NG�X���b�h�\���ݒ肪���[�U�[�ɂ���Đݒ肳��Ă��Ȃ�����
# �f�t�H���g�l��ݒ肵�܂�
# 0 : �X���b�h���\���ɂ���
# 1 : �X���b�h����u������
$ngthread_default_display_mode = 0;

# �X���b�h�쐬�҂�NG�ݒ� �����v�ݒ�
# �X���b�h�쐬�Җ��ɂ��̐ݒ�l�̕�����̂����ꂩ���܂܂��ꍇ�A
# �X���b�h�ꗗ��ʂ̃X���b�h�쐬�҂�NG�ݒ�ł��̐ݒ�l�Ɠ�����������܂݁A
# ���s�S�̂̐ݒ�ɂ���v�����ꍇ��NG�X���b�h�Ƃ��Ĕ��肵�܂�
@ngthread_thread_creator_must_include_strings = (
);

# ���X���e���X���b�h�쐬�Җ��㏑�� �Ώۃ��X�͈͐ݒ�
# ���X���e���ɁA���XNo.�� >>2���炱�̐ݒ�l�܂łƂȂ�ꍇ��
# >>1�ƃz�X�g�܂��͓o�^ID�A�܂���CookieA�A�܂��͏���ID�������ꍇ��
# �X���b�h�ꗗ��ʂł̃X���b�h�쐬�Җ����������ݎ��̖��O�ŏ㏑�����܂�
$ngthread_thread_list_creator_name_override_max_res_no = 7;

# ���X���e���X���b�h�쐬�Җ��㏑�� ���O���e�Җ��ݒ�
# ���X���e���ɃX���b�h�쐬�Җ��㏑���̑ΏۂƂȂ��Ă��A
# �������ݎ��̖��O�� ���̐ݒ�l�̂����ꂩ�̕�������܂ޏꍇ�́A
# �㏑���̑Ώۂ��珜�O���܂�
@ngthread_thread_list_creator_name_override_exclude_names = (
);

# ���X���e���X���b�h�쐬�Җ��㏑�� ���菜�O�z�X�g�ݒ�
# ���X���e���ɃX���b�h�쐬�Җ��㏑���̑Ώ۔��莞��
# ���̐ݒ�l�̂����ꂩ�̕�������܂ރz�X�g�̏ꍇ�́A����z�X�g������s���܂���
@ngthread_thread_list_creator_name_override_exclude_hosts = (
);

#-------------------------------------------------
#  �����[�U�����\���@�\
#  �@UserAgent�̋����\���@�\ �ݒ荀��
#-------------------------------------------------

# �O�����O�t�@�C��(JSON)�p�X
$highlight_userinfo_log_path = './highlight_userinfo.json';

# ���[�U�����\���@�\ �L�^��� �ێ�����
$highlight_userinfo_hold_hour = "336";

# UserAgent�̋����\���@�\ �L�^��� �ێ�����
$highlight_ua_hold_hour = "336";

#-------------------------------------------------
#  ���Ǘ���� ����ݒ�@�\
#-------------------------------------------------

# �Ǘ���ʂł̓���ݒ�@�\�̗��p
# 0 : ����ݒ�@�\�𗘗p���Ȃ�
# 1 : ����ݒ�@�\�𗘗p����
$conf_override = 1;

# ����ݒ�̋L�^�t�@�C���p�X
# �yinit.cgi���猩���p�X���w�肵�ĉ������z
$conf_override_path = "./init-override.cgi";

#-------------------------------------------------
#  ��WebProtect�A�g �o�^ID�F�؋@�\
#-------------------------------------------------

# �V�K�X���b�h�쐬�t�H�[���ł�WebProtect�o�^ID�F�؋@�\�̗��p
# 0 : �o�^ID�F�؋@�\�𗘗p���Ȃ�
# 1 : �o�^ID�F�؋@�\�𗘗p����
$webprotect_auth_new = 0;

# �X���b�h���ԐM�t�H�[���ł�WebProtect�o�^ID�F�؋@�\�̗��p
# 0 : �o�^ID�F�؋@�\�𗘗p���Ȃ�
# 1 : �o�^ID�F�؋@�\�𗘗p����
$webprotect_auth_res = 0;

# �F�؎��ɓo�^ID��������Ȃ��������̃G���[���b�Z�[�W
$webprotect_auth_id_notfound_msg = "�o�^ID��������Ȃ����A�o�^�p�X���[�h������������܂���B";

# �F�؎��ɓo�^�p�X���[�h���������Ȃ��������̃G���[���b�Z�[�W
$webprotect_auth_pass_mismatch_msg = "�o�^ID��������Ȃ����A�o�^�p�X���[�h������������܂���B";

# WebProtect �f�B���N�g���p�X
# �y����init.cgi���猩���p�X���w�肵�ĉ������z
$webprotect_path = '../protect';

# �o�^ID�F�ؐ������O�@�\�̗��p
# �X���b�h�쐬���E���X���e���ɔF�؂ɐ��������o�^ID���L�^���܂�
# 0 : �o�^ID�F�ؐ������O�@�\�𗘗p���Ȃ�
# 1 : �o�^ID�F�ؐ������O�@�\�𗘗p����
$webprotect_authlog = 1;

# �o�^ID�F�ؐ������O�@�\���O�t�@�C���p�X
# �y����init.cgi���猩���p�X���w�肵�ĉ������z
$webprotect_authlog_path = './kakikomi.log';

#-------------------------------------------------
#  ���A�b�v���[�h���Ȃ��摜��MD5�n�b�V���l�ݒ�
#-------------------------------------------------

# �A�b�v���[�h���Ȃ��摜 MD5�n�b�V���l�ݒ�
# �A�b�v���[�h���悤�Ƃ���摜��MD5�������Ŏw�肵���l�ɍ��v����ꍇ�ɖ������A
# �A�b�v���[�h���Ȃ��������̂Ƃ��Ď�舵���܂�
@ignore_img_md5hash = (
);

#-------------------------------------------------
#  ���A�b�v���[�h�֎~�摜�w��@�\
#-------------------------------------------------

# �A�b�v���[�h�֎~�`�F�b�N�ʉ߉摜 MD5�n�b�V���l���O�t�@�C���p�X
# �A�b�v���[�h�ɐ��������t�@�C����MD5�n�b�V���l�̃��O�t�@�C���p�X��ݒ肵�܂�
$img_md5hash_log_path = './img_md5hash.log';

# �A�b�v���[�h�֎~�摜�t�@�C�� MD5�n�b�V���l�ݒ�
# �֎~�摜�Ƃ��Č��m����A�I���W�i���摜�t�@�C����MD5�n�b�V���l��ݒ肵�܂�
# ���͗�: 'd41d8cd98f00b204e9800998ecf8427e',
@prohibit_img_md5hash = (
);

#-------------------------------------------------
#  ������摜�A�b�v���[�h�֎~�@�\
#-------------------------------------------------

# ����摜�A�b�v���[�h�֎~�@�\�̗��p
# �A�b�v���[�h�摜��MD5���`�F�b�N���A
# �����l�̃A�b�v���[�h�摜����������ꍇ�ɃG���[��ʂ�\�����܂�
# 0 : ����摜�A�b�v���[�h�֎~�@�\�𗘗p���Ȃ� (�`�F�b�N���Ȃ�)
# 1 : ����摜�A�b�v���[�h�֎~�@�\�𗘗p����
$prohibit_same_img_upload = 1;

#-------------------------------------------------
#  ���d�����e����
#-------------------------------------------------

# �d�����e�����̑ΏۂƂ���X���b�h����ݒ肵�܂�
# �X���b�h���̎w�蕶����̐擪�Ɂu!�v��ǉ������ꍇ�́A
# �ݒ�Ɉ�v���Ȃ����̂�ΏۂƂ��܂��B
#
@duplicate_post_restrict_thread = (
);

#-------------------------------------------------
#  ���L�[���[�h��v���� �ݒ荀��
#-------------------------------------------------
# �ϐ� �O���t�@�C���p�X
$match_variable_settings_filepath = './match_variable_settings.csv';

# �Ђ炪�ȁE�J�^�J�i ���胂�[�h�ݒ�
# �ݒ�l�̂Ђ炪�ȁE�J�^�J�i�ŁA�S�p�Ɣ��p����ʂ��Ȃ��ň�v������s���ȊO��
# �啶���Ə���������ʂ��Ȃ��ň�v������s�����ǂ�����ݒ肵�܂�
# 0 : �Ђ炪�ȁE�J�^�J�i�̑S/���p�̂݋�ʂ����ɔ��肵�܂� (��/�������͋�ʂ���܂�)
# 1 : �Ђ炪�ȁE�J�^�J�i�̑S/���p�Ƒ�/��������S�ċ�ʂ����ɔ��肵�܂�
$match_hiragana_katakana_normalize_mode = 1;

#-------------------------------------------------
#  �����񏑂����݂܂ł̎��Ԑ����@�\
#-------------------------------------------------
# �O���t�@�C���p�X
$firstpost_restrict_settings_filepath = './firstpost_restrict_settings.csv';

# ���񏑂����݂܂ł̎��Ԑ����@�\ �ΏۊO���[�U�[�ݒ�
# �����Ώۂ��珜�O���郆�[�U�[��
# �u�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID�v�̂悤�Ɏw�肵�܂�
@firstpost_restrict_exempt = (
);

#-------------------------------------------------
#  �����O����\���@�\
#-------------------------------------------------

# ���O�����\���ɂ���X���b�h�̃X���b�h����
# �u,�v��؂�Őݒ肵�܂�
@hide_form_name_field = (
);

#-------------------------------------------------
#  �����e���̖��O�̏����@�\
#-------------------------------------------------
#
# ���e���ɖ��O����������Ώۂ̓��e��
# '�X���b�h��:���O:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID' �̃��X�g�Őݒ肵�܂�
#
# �X���b�h���E���O�E�z�X�g���EUserAgent�͕�����v�ACookieA or �o�^ID�͊��S��v�Ŕ�����s���܂�
#
# �X���b�h���̎w�蕶����̐擪�Ɂu!�v��ǉ������ꍇ�́A
# �ݒ�Ɉ�v���Ȃ����̂�ΏۂƂ��܂��B
#
# ���O�ɁA�u��hogehoge�v�ȂǂŁu���v���܂ޏꍇ�́A�g���b�v�ϊ���̖��O�ň�v������s���܂�
# �܂��A�u#hogehoge�v�ȂǂŁu#�v���܂ޏꍇ�́A�g���b�v�ϊ��̖��O�ň�v������s���܂�
#
# �z�X�g����UserAgent�̑g�ݍ��킹�ECookieA or �o�^ID�E����ID�̎w�蕶����ł́A
# �����L�q���Ȃ������ꍇ��u-�v�݂̂�ݒ肵���ꍇ�́A���̍��ڂɂ��Ĕ�����s���܂���B
# �܂��A�w�蕶����̐擪�Ɂu!�v��ǉ������ꍇ�́A�ݒ�Ɉ�v���Ȃ����̂�ΏۂƂ��܂��B
#
# �z�X�g����UserAgent�̑g�ݍ��킹�̎w�蕶����ł́A
# �z�X�g����UserAgent���u<>�v�ŋ�؂��ċL�q���܂����A
# �u<>�v���܂܂�Ȃ��ꍇ�́A�z�X�g���Ƃ��ĔF�����A�S�Ă�UserAgent�Ɉ�v���܂��B
# �܂��A�z�X�g����UserAgent�̑g�ݍ��킹�w����u���v�ŋ�؂�ƁA
# ���ꂼ��̎w��̂����ꂩ�Ɉ�v�����ꍇ�ɑΏۂƂ��Ĕ��肵�܂��B
#
# ���̑��A�X���b�h���E���O�E�z�X�g����UserAgent�̑g�ݍ��킹�̐ݒ�t�H�[�}�b�g�ɂ��āA
# �����������݋֎~�@�\�Ɠ��l�ƂȂ�܂�
#
@remove_name_on_post = (
);

#-------------------------------------------------
#  ���z�X�g�Ȃǂɂ��摜�A�b�v���[�h�̖���
#-------------------------------------------------
# �摜�A�b�v���[�h���������Ȃ����[�U�[��
# '�X���b�h��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:������' �̃��X�g�Őݒ肵�܂�
@disable_img_upload = (
);

#-------------------------------------------------
#  ���z�X�g�Ȃǂɂ��age�̖���
#-------------------------------------------------
# �����I��sage���e�����郆�[�U�[��
# '�X���b�h��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:������' �̃��X�g�Őݒ肵�܂�
@disable_age = (
);

#-------------------------------------------------
#  ���z�X�g�Ȃǂɂ�郆�[�U�ԃ��[���̘A�����M�����@�\
#-------------------------------------------------

# ���[�����M�����ۂ��郆�[�U�[
# '�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:������' �̃��X�g�Őݒ肵�܂�
@usermail_prohibit = (
);

# mail.log($mailfile)�ɋL�^���Ȃ����[�U�[
# '�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:������' �̃��X�g�Őݒ肵�܂�
@usermail_not_record = (
);

# �������X�̑��M�𐧌����鎞�� (�P��:�b)
$usermail_time_of_continuously_send_restricting = 180;

# ���[�����M��A�h���X
$usermail_to_address = 'hoge@example.com';

#-------------------------------------------------
#  ���X���b�h�{�������@�\ �ݒ荀��
#-------------------------------------------------

# �X���b�h�{�������Ώۃ��[�U�[
# '����:�X���b�h��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:CookieA�̗L��:���t�ɂ�鏜�O:CookieA or �o�^ID or ����ID�̏��O:������' �̃��X�g�Őݒ肵�܂�
# (�擪�́u�����v�̃t�B�[���h�� �� ���Z�b�g����Ă���ݒ�́A�����Ώ۔�����s���܂���)
@thread_browsing_restrict_user = (
);

# �X���b�h�{�������Ώێ����_�C���N�g��URL
$thread_browsing_restrict_redirect_url = 'http://hogehoge.com/';

#-------------------------------------------------
#  ���O���t�@�C���ɂ�鎩���֎~�@�\�Ȃǂ̓���
#-------------------------------------------------

# �O���t�@�C���p�X
$prohibit_suppress_settings_filepath = './prohibit_suppress_settings.csv';

#-------------------------------------------------
#  �������������݋֎~�@�\
#-------------------------------------------------

# �����������݋֎~�@�\ �������O�t�@�C��(CSV)�p�X
$auto_post_prohibit_log_path = './auto_prohibit.csv';

# �����������݋֎~�@�\ �ݐσ��O�t�@�C��(CSV)�p�X
$auto_post_prohibit_no_delete_log_path = './auto_prohibit_no_delete.csv';

# �����������݋֎~�@�\ �������O �������� (�P��:�b)
# �����������݋֎~�@�\���莞�ɏ������Ԃ��o�߂��Ă��郍�O�𔻒肩�珜�O���A
# ���O�������ݎ��Ɏ����������܂�
# �܂��A0�ɐݒ肷��Ǝ����������܂���
$auto_post_prohibit_delete_time = 300;

# �����������݋֎~�@�\ �������݋֎~�Ώێ� ���_�C���N�g��URL
# ���΃p�X�w�莞�ɂ́Aregist.cgi���猩��URL�ɕϊ����ă��_�C���N�g���܂�
# ���w�莞�ɂ̓��_�C���N�g���s���܂���
$auto_post_prohibit_redirect_url = './patio.cgi';

# �����������݋֎~�@�\ ���X�ԐM�� ���OURL��o�� �擪������
@auto_post_prohibit_log_concat_url = ('http://hogehoge.com/read.cgi?no=');

# �X���b�h�^�C�g��(�ے����)�E�ϊ��O/�ϊ���摜��MD5�E��v�����O�o�̓R�����g�E�z�X�g����UserAgent�ECookieA or �o�^ID or ����ID�̑g�ݍ��킹
@auto_post_prohibit_combination_imgmd5 = (
);

## �����������݋֎~�@�\ �����������O���ݎ����_�C���N�g�̔���v�f�ǉ� �Ώۃz�X�g�ݒ� ##
# �����������O�ƃz�X�g����v�����ꍇ�ɁA
# ����ɁACookieA����v����K�v������z�X�g��ݒ肵�܂�
# �z�X�g�͒��Ԉ�v�Ŕ��肵�܂�
@auto_post_prohibit_additional_match_required_host = (
);

## �����������݋֎~�@�\ ���O���̏��O�@�\ ##
#
# ���̐ݒ�l�ɍ��v���閼�O�̓��e�̏ꍇ�́A
# �u�����������݋֎~�@�\(���O)�v�̔�����s���܂���
$auto_post_prohibit_exempting_name = '';

## �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\ ##
#
# ���O�t�@�C��(JSON)�p�X
$auto_post_prohibit_thread_number_res_target_log_path = './auto_prohibit_thread_number_res_target.json';

# [�ݒ莞��1]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_1 = "1";

# [�ݒ莞��2]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_2 = "2";

# [�ݒ莞��3]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_3 = "3";

# [�ݒ莞��4]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_4 = "4";

# [�ݒ莞��5]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_5 = "5";

# [�ݒ莞��6]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_number_res_target_hold_hour_6 = "6";

## �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\ ##
#
# ���O�t�@�C��(JSON)�p�X
$auto_post_prohibit_thread_title_res_target_log_path = './auto_prohibit_thread_title_res_target.json';

# [�ݒ莞��1]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_1 = '1';

# [�ݒ莞��2]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_2 = '2';

# [�ݒ莞��3]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_3 = '3';

# [�ݒ莞��4]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_4 = '4';

# [�ݒ莞��5]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_5 = '5';

# [�ݒ莞��6]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$auto_post_prohibit_thread_title_res_target_hold_hour_6 = '6';

# ���X���e �����P�� (�u�����������݋֎~�@�\(���X)�v�̃��X���e�ɑ���)
# �����P��1
$auto_post_prohibit_thread_title_res_target_restrict_keyword = '';

# �����P��2
$auto_post_prohibit_thread_title_res_target_restrict_keyword_2 = '';

# �����P��3
$auto_post_prohibit_thread_title_res_target_restrict_keyword_3 = '';

# �����P��4
$auto_post_prohibit_thread_title_res_target_restrict_keyword_4 = '';

# �����P��5
$auto_post_prohibit_thread_title_res_target_restrict_keyword_5 = '';

# �����P��6
$auto_post_prohibit_thread_title_res_target_restrict_keyword_6 = '';

# �����P��7
$auto_post_prohibit_thread_title_res_target_restrict_keyword_7 = '';

# �����P��8
$auto_post_prohibit_thread_title_res_target_restrict_keyword_8 = '';

# �����P��9
$auto_post_prohibit_thread_title_res_target_restrict_keyword_9 = '';

# �����P��10
$auto_post_prohibit_thread_title_res_target_restrict_keyword_10 = '';

# �����P��11
$auto_post_prohibit_thread_title_res_target_restrict_keyword_11 = '';

# �����P��12
$auto_post_prohibit_thread_title_res_target_restrict_keyword_12 = '';

# �����P��13
$auto_post_prohibit_thread_title_res_target_restrict_keyword_13 = '';

# �����P��14
$auto_post_prohibit_thread_title_res_target_restrict_keyword_14 = '';

# �����P��15
$auto_post_prohibit_thread_title_res_target_restrict_keyword_15 = '';

# �����P��16
$auto_post_prohibit_thread_title_res_target_restrict_keyword_16 = '';

# �����P��17
$auto_post_prohibit_thread_title_res_target_restrict_keyword_17 = '';

# �����P��18
$auto_post_prohibit_thread_title_res_target_restrict_keyword_18 = '';

# �����P��19
$auto_post_prohibit_thread_title_res_target_restrict_keyword_19 = '';

# �����P��20
$auto_post_prohibit_thread_title_res_target_restrict_keyword_20 = '';

# ���X���e �������O�P�� (�����P��N�Ə��O�P��N���Ή����܂�)
# ���O�P��1
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword = '';

# ���O�P��2
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_2 = '';

# ���O�P��3
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_3 = '';

# ���O�P��4
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_4 = '';

# ���O�P��5
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_5 = '';

# ���O�P��6
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_6 = '';

# ���O�P��7
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_7 = '';

# ���O�P��8
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_8 = '';

# ���O�P��9
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_9 = '';

# ���O�P��10
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_10 = '';

# ���O�P��11
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_11 = '';

# ���O�P��12
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_12 = '';

# ���O�P��13
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_13 = '';

# ���O�P��14
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_14 = '';

# ���O�P��15
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_15 = '';

# ���O�P��16
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_16 = '';

# ���O�P��17
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_17 = '';

# ���O�P��18
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_18 = '';

# ���O�P��19
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_19 = '';

# ���O�P��20
$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_20 = '';

# �w�肵�����XNo�܂ł̎����������݋֎~�@�\
# �u���X�ԍ�:�X���b�h��:���X1�̏��O�P��:�����P��:���������O:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:���Ԏw��:�������v�̂悤�Ɏw�肵�܂�
# �X���b�h���E�z�X�g��UserAgent�̑g�ݍ��킹�̎w��ł́A�擪�u!�v�ɂ��ے�����̗��p���\�ł�
@auto_post_prohibit_up_to_res_number = (
);

## �����񓊍e���̎����������݋֎~�@�\ ##

# �����Ώېݒ�
# �u����:�X���b�h��:���X1�̏��O�P��:�����P��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:���Ԏw��:�������v�̂悤�Ɏw�肵�܂�
# �X���b�h���E�z�X�g��UserAgent�̑g�ݍ��킹�̎w��ł́A�擪�u!�v�ɂ��ے�����̗��p���\�ł�
@auto_post_prohibit_multiple_submissions = (
);

# ���[�U�[���e�J�E���g���O �t�@�C���p�X
$auto_post_prohibit_multiple_submissions_count_log_path = './auto_post_prohibit_multiple_submissions.log';

# ���_�C���N�g���铯�ꃆ�[�U�[���e��
# �������[�U�[�����̐��ȏ�̓��e���s���Ă���ꍇ�A���_�C���N�g�ΏۂƂ��Ĕ��肵�܂�
$auto_post_prohibit_multiple_submissions_redirect_threshold = 4;

# ���[�U�[���e�J�E���g���O �������� (�P��:��)
# �����񓊍e���̎����������݋֎~�@�\�̔��莞��
# �������Ԃ��o�߂��Ă��郍�O�𔻒肩�珜�O���A���O�������ݎ��Ɏ����������܂�
$auto_post_prohibit_multiple_submissions_log_hold_minutes = 60;

## �ÃX��age�̎����������݋֎~�@�\ ##

# �����Ώېݒ�
# �u����:�X���b�h��:���O���X�������ԑO:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:���Ԏw��:�������v�̂悤�Ɏw�肵�܂�
# �X���b�h���E�z�X�g��UserAgent�̑g�ݍ��킹�̎w��ł́A�擪�u!�v�ɂ��ے�����̗��p���\�ł�
@auto_post_prohibit_old_thread_age = (
);

# ���[�U�[�ÃX��age���e�J�E���g���O �t�@�C���p�X
$auto_post_prohibit_old_thread_age_count_log_path = './auto_post_prohibit_old_thread_age.log';

# ���_�C���N�g���铯�ꃆ�[�U�[���e��
# �������[�U�[�����̐��ȏ�̌ÃX��age���e���s���Ă���ꍇ�A���_�C���N�g�ΏۂƂ��Ĕ��肵�܂�
$auto_post_prohibit_old_thread_age_redirect_threshold = 4;

# ���[�U�[�ÃX��age���e�J�E���g���O �������� (�P��:��)
# �ÃX��age�̎����������݋֎~�@�\�̔��莞��
# �������Ԃ��o�߂��Ă��郍�O�𔻒肩�珜�O���A���O�������ݎ��Ɏ����������܂�
$auto_post_prohibit_old_thread_age_log_hold_minutes = 60;

#-------------------------------------------------
#  ���O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓���
#-------------------------------------------------

# �O���t�@�C���p�X
$thread_create_post_restrict_settings_filepath = './thread_create_post_restrict_settings.csv';

#-------------------------------------------------
#  ���X���b�h��ʂ��烆�[�U�𐧌�����@�\
#-------------------------------------------------

# ���O�t�@�C��(JSON)�p�X
$restrict_user_from_thread_page_target_log_path = './restrict_user_from_thread_page_target.json';

## �ݒ莞��1 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_1 = '1';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_1 = '�ݒ莞��1 1h';

## �ݒ莞��2 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_2 = '3';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_2 = '�ݒ莞��2 3h';

## �ݒ莞��3 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_3 = '6';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_3 = '�ݒ莞��3 6h';

## �ݒ莞��4 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_4 = '24';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_4 = '�ݒ莞��4 1day';

## �ݒ莞��5 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_5 = '72';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_5 = '�ݒ莞��5 3day';

## �ݒ莞��6 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_6 = '168';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_6 = '�ݒ莞��6 7day';

## �ݒ莞��7 ##
# �ݒ�ێ�����
$restrict_user_from_thread_page_target_hold_hour_7 = '720';
# �ǉ������N�E�v���_�E�����j���[�\����
$restrict_user_from_thread_page_target_type_name_7 = '�ݒ莞��7 30day';

#-------------------------------------------------
#  ���X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
#-------------------------------------------------

# ���O�t�@�C��(JSON)�p�X
$restrict_user_from_thread_page_by_time_range_target_log_path = './restrict_user_from_thread_page_by_time_range_target.json';

# [�ݒ莞��1]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$restrict_user_from_thread_page_by_time_range_target_hold_hour_1 = '72';

# [�ݒ莞��2]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$restrict_user_from_thread_page_by_time_range_target_hold_hour_2 = '168';

# [�ݒ莞��3]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$restrict_user_from_thread_page_by_time_range_target_hold_hour_3 = '336';

# [�ݒ莞��4]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$restrict_user_from_thread_page_by_time_range_target_hold_hour_4 = '504';

# �������Ԕ͈�
# HHmm-HHmm(����00�`23 ����00�`59)�̏����Ŏw�肵�܂��B
# �܂��A���Ԕ͈͂̎n�߂��I��������Ɏw�肳��Ă���ꍇ�A���Ԕ͈͏I���𗂓��̎����Ƃ��Ď�舵���܂��B
# ��: �u2300-0600�v�Ǝw�肵���ꍇ�A����23:00:00�`����06:00:59�܂ł𔻒�Ώێ��ԂƂ��܂��B
$restrict_user_from_thread_page_by_time_range_enable_time_range = '0000-0600';

#-------------------------------------------------
#  ���X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
#-------------------------------------------------

# ���O�t�@�C��(JSON)�p�X
$in_thread_only_restrict_user_from_thread_page_target_log_path = './in_thread_only_restrict_user_from_thread_page_target.json';

# [�ݒ莞��]���N���b�N���Ēǉ������ꍇ�̐ݒ�ێ�����
$in_thread_only_restrict_user_from_thread_page_target_hold_hour = '336';

#-------------------------------------------------
#  ���X���b�h�쐬�E���X����reCAPTCHA�F�؋@�\
#-------------------------------------------------

# reCAPTCHA Site Key �ݒ�
$recaptcha_site_key = "6LdmHRATAAAAAKr58AhPfczV1py1w73eNk3jtHKw";

# reCAPTCHA Secret Key �ݒ�
$recaptcha_secret_key = "6LdmHRATAAAAAOG8FHjpINMRdkaWx1lixmh9jCV7";

# �X���b�h�쐬����reCAPTCHA�F�؋@�\�̗��p
# 0 : ���p���Ȃ�
# 1 : ���p����
$recaptcha_thread = 0;

# �X���b�h�쐬���̏������O(�X���b�h�쐬�J�E���g���O)�p�X
$recaptcha_thread_create_log = "./recaptcha_thread_create_log.csv";

# �X���b�h�A���쐬���J�E���g���� (�P��:�b)
# �{�@�\�̃X���b�h�쐬�J�E���g���O��
# ���̎��Ԃ𒴂������O�ɂ��Ď�����������܂�
# �܂��A0�ɐݒ肷��Ǝ����������܂���
$recaptcha_thread_count_time = 600;

# �X���b�h�A���쐬���e��
# �X���b�h�A���쐬���J�E���g���ԓ���
# ���̐��𒴂��ăX���b�h�쐬���s�����Ƃ���ƁAreCAPTCHA�F�؂̑ΏۂƂȂ�܂�
#
# ��: �ݒ�l��5��ݒ肵���ꍇ�A
#     �A���쐬���J�E���g���ԓ���5���̃X���b�h�쐬�����������
#     �X���b�h�쐬�t�H�[����\�����鎞��reCAPTCHA���\������܂�
$recaptcha_thread_permit = 5;

# �X���b�h�쐬���̗ݐσ��O�p�X
# �X���b�h�쐬���̍폜���O�Ɠ����e�Ŏ����������s��Ȃ����O�ł�
$recaptcha_thread_create_log_no_delete = "./recaptcha_thread_create_log_no_delete.csv";

# �X���b�h�쐬����reCAPTCHA�F�ؑΏۃz�X�g���O�p�X
$recaptcha_thread_auth_host_log = "./recaptcha_thread_auth_host_log.csv";

# �X���b�h�쐬����reCAPTCHA�F�ؑΏۃz�X�g���O �������� (�P��:�b)
# reCAPTCHA�F�ؑΏۃz�X�g�ŏ������݂Ő��������ꍇ��
# �������Ԃ��o�߂��Ă����ꍇ�́A���O����������܂�
# �܂��A0�ɐݒ肷��Ǝ����������܂���
$recaptcha_thread_auth_host_release_time = 300;

# ���X����reCAPTCHA�F�؋@�\�̗��p
# 0 : ���p���Ȃ�
# 1 : ���p����
$recaptcha_res = 0;

#-------------------------------------------------
#  ����������reCAPTCHA�F�؋@�\
#-------------------------------------------------

# reCAPTCHA Site Key �ݒ�
$find_recaptcha_site_key = $recaptcha_site_key;

# reCAPTCHA Secret Key �ݒ�
$find_recaptcha_secret_key = $recaptcha_secret_key;

# ��������reCAPTCHA�F�؋@�\�̗��p
# 0 : ���p���Ȃ�
# 1 : ���p����
$find_recaptcha = 0;

# �A���������J�E���g���� (�P��:�b)
# �{�@�\�̌������J�E���g���O��
# ���̎��Ԃ𒴂������O�ɂ��Ď�����������܂�
# �܂��A0�ɐݒ肷��Ǝ����������܂���
$find_recaptcha_count_time = 600;

# �A���������e��
# �A���������J�E���g���ԓ���
# ���̐��𒴂��Č������s�����Ƃ���ƁAreCAPTCHA�F�؂̑ΏۂƂȂ�܂�
#
# ��: �ݒ�l��5��ݒ肵���ꍇ�A
#     �A���������J�E���g���ԓ���5��̌��������������
#     �����t�H�[����\�����鎞��reCAPTCHA���\������܂�
$find_recaptcha_permit = 5;

# ��������reCAPTCHA�F�ؑΏۃz�X�g���O �������� (�P��:�b)
# reCAPTCHA�F�ؑΏۃz�X�g�ŏ������݂Ő��������ꍇ��
# �������Ԃ��o�߂��Ă����ꍇ�́A���O����������܂�
# �܂��A0�ɐݒ肷��Ǝ����������܂���
$find_recaptcha_auth_host_release_time = 300;

# �����������O(�������J�E���g���O)�p�X
# �ݐό������O�p�X�́A$srchlog �Őݒ肵�܂�
$find_recaptcha_count_log = "./recaptcha_find_log.csv";

# ��������reCAPTCHA�F�ؑΏۃz�X�g���O�p�X
$find_recaptcha_auth_host_log = "./recaptcha_find_auth_host_log.csv";

# ���������������reCAPTCHA�F�؃X�L�b�v�@�\�̗��p
# 0 : ���p���Ȃ�
# 1 : ���p����
$find_recaptcha_continue = 0;

# ������� �A���������J�E���g���� (�P��:�b)
# ��������ł̃y�[�W�J�ڂɂ��A���������J�E���g���܂�
# ���̎��Ԃ𒴂��������̓J�E���g���珜�O�E��������܂�
$find_recaptcha_continue_count_time = 600;

# ������� �A���������e��
# $find_recaptcha_permit�𒴂��������ł��A
# ����������{�ݒ�l�ȓ��ł���΁AreCAPTCHA�F�؂��X�L�b�v���܂�
$find_recaptcha_continue_permit = 3;

### ���������������reCAPTCHA�F�؃X�L�b�v Cookie�Í��� ###
# ���������������reCAPTCHA�F�؂��X�L�b�v���邽�߁A
# �Z�b�V����Cookie�Ɍ����������Í����ۑ����ė��p���܂�
#
# *** 2048bit�ȏ� *** �̌���������RSA�����Aopenssl�R�}���h��A
# http://travistidwell.com/jsencrypt/demo/ �Ȃǂ�Web�T�C�g��ō쐬���A
# �閧���E���J�������ꂼ��ݒ肵�ĉ�����
#
# ���͕����s�ɓn��܂��̂ŁA�N�H�[�e�[�V�����Ԃɂ��̂܂ܓ\��t���ĉ�����
#
# �閧�� (-----BEGIN RSA PRIVATE KEY----- �� -----END RSA PRIVATE KEY----- ���܂߂Ă��̂܂ܓ\��t���ĉ�����)
$find_recaptcha_continue_cookie_rsa_private_key = '
-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQBDTneEMi3GdlcsWOMbr+8S+oT+GJcdgSsMOCfg2loSNCIaS1OF
qC8SCjgTVqPGF9kvl/Ohs4aSZPIjeGHl9w5Z22XSrGSnh0xCKkTT7mCQ0qrNivkC
EpDSF0KHU2YTvKzML45fW4x6ssuPx1D1334GNEmuyKTdqvkkcJtro46K+hg+3YFO
5G5KobSnGbcRmtNO/UOoMaW7NJgAwEYssObOsZL5uWGsTKn1HR5gndzAkctr8Fo/
+/zQ6pTolm34AnbK5D2vQDGzQFxQvAxJs17khzCk2e2gdbmmVAtsqBlVI2EqXIkY
L6G3lo7CVvSZH52OD684JLAvlR9HdO034nWNAgMBAAECggEAMAhlfrAYvtNhbsKY
gP/TS+YA1x1Rarrtr7C7tNnfAbK2y7EKEA5wWR1120cvZYVLd42nTrTByuPDcdDN
fMINOc87IVfqFSyXHXjw2ZX60B+nyTvubK43L9dtoQnBhUBWyPj/T8oTvNSwNRF3
E6DFXUQfeV6zWYZUes7p+60jYsZQ8z0jIKgRdWCx/v88DRJiBLONLK7WWJOg+3o+
z5n9teg524rMm+NQ+7s7ZPY4q4G69LlQvq9Qb3rM41FuuaYJSN0swBeI2aU3nGQB
zr4Ab9XrvZv/2fA/Ljy1v//SsqUoPPkyvO9km0tvD3nyiWAb9ZPyV6PDz7mCPrvO
+6+GuQKBgQCGXKpW0gp5nx+Lwlo+OQqCWihqfy9skNHdYLw2ZHcMgqIkQ/JylhoH
TwYmFfs9oxFHeWP+IPT0SNky6agW7S3XHgUdarn0jW7IEVrtZiqas5fA7udcBgG+
zgN+WqjDDBGkgFE6kiOyImjDCN+LojLxEYOW2/jJIA9WAu7Q1XZ5SwKBgQCAPTmq
pcbA9V5HPad98hcXkLX3iZAVEKCHPm0IXFvkLApEROLWZaRWyjx1NXcpyOZjLhar
ZpbDhuwxdJFX6YOcA5TtmN7zIJizmjtweV6UlS0/G5f2OvAz0ovMHHy2HVM6qmiU
DzbUV6T/bxuNVbZx7oTZOtkApaJY+yUCyCEdhwKBgCXwOmTDcBPBW33yBds17gK6
hFj1yqVECw4QR3SwT3En3bKRwP6b5YOUy66rXEKeLb3Zx+M02RW1ECcxFLZMiDoK
jvUsco9b9CDnzZ3k0DjYZwwiKQ+x3oJK12+xF5/jY4Poe4cnRo8A6kXP1pct2GZ7
RIWvXQMlW081CsvKymYbAoGAaShLmmi4U9ChT8/6Aeg8EWHkJalTUkLBMEX7iMib
vb5zaMoILQFKQrUx4HdIUSZh7eCETGciqBGCq4dIDAv7lTrGrBMYd8w6C8UkirWr
3jF52e8ZrJtmD0jOxEBz766aalgEy6yyLGv2bFPDByHLKyAJJk0AV2x7dXX0QpSz
uw8CgYAuFwME4Bzg9Fd4+N0WC9mFbg4631VjaG35oFTOCMJqYKbkmPANWKWUl+Ak
cPtpEeXSsqUxyO2UmTD7XYTOLj+IvKp9KXWtMIOhqIvSXpJ0pKgOJ3Z5mvhhlTme
m50WX8g+3i5mxKgbaH8qA01Bu8Q6vFRMpLSyNHMGDGi57Q0s2Q==
-----END RSA PRIVATE KEY-----
';
#
# ���J�� (�閧���Ɠ��l�ɁA�J�n�s�E�I���s���܂߂Ă��̂܂ܓ\��t���ĉ�����)
# -----BEGIN PUBLIC KEY----- �� -----END PUBLIC KEY----- �̌`���A�������́A
# -----BEGIN RSA PUBLIC KEY----- �� -----END RSA PUBLIC KEY----- �̌`�������p�\�ł�
$find_recaptcha_continue_cookie_rsa_public_key = '
-----BEGIN PUBLIC KEY-----
MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQBDTneEMi3GdlcsWOMbr+8S
+oT+GJcdgSsMOCfg2loSNCIaS1OFqC8SCjgTVqPGF9kvl/Ohs4aSZPIjeGHl9w5Z
22XSrGSnh0xCKkTT7mCQ0qrNivkCEpDSF0KHU2YTvKzML45fW4x6ssuPx1D1334G
NEmuyKTdqvkkcJtro46K+hg+3YFO5G5KobSnGbcRmtNO/UOoMaW7NJgAwEYssObO
sZL5uWGsTKn1HR5gndzAkctr8Fo/+/zQ6pTolm34AnbK5D2vQDGzQFxQvAxJs17k
hzCk2e2gdbmmVAtsqBlVI2EqXIkYL6G3lo7CVvSZH52OD684JLAvlR9HdO034nWN
AgMBAAE=
-----END PUBLIC KEY-----
';

#-------------------------------------------------
#  ���\�����e����@�\
#-------------------------------------------------
# �X���b�h�y�[�W�ŕ\���͈͂̃��X��
# �ݒ肵����������܂ނ��A�摜�A�b�v�`�F�b�N���L���̏ꍇ�͉摜���܂܂�Ă���ꍇ�ɁA
# �\�����e��ύX���ďo�͂��܂�

# �\�����e����@�\ �Ώە�����ݒ�
@contents_branching_keyword = ('�e���v���[�g');

# �\�����e����@�\ �摜�A�b�v�`�F�b�N
# 0 : �`�F�b�N���Ȃ�
# 1 : �`�F�b�N����
$contents_branching_img_check = 1;

#-------------------------------------------------
#  ���������݃��O�o�͋@�\
#-------------------------------------------------
# �X���b�h�쐬/���X�ԐM�ɂ�鏑�����݃��O���o�͂��܂�

# �������݃��O�o�͋@�\�̗��p
# 0 : ���p���Ȃ�
# 1 : ���p����
$post_log = 1;

# �������݃��O �o�̓f�B���N�g���p�X
# ���̃f�B���N�g���͗\�ߍ쐬���A�p�[�~�b�V�������������݉\�ɐݒ肵�ĉ�����
$post_log_dir = './kakikomi';

# �������݃��O�t�@�C���� ����������
# �������݃��O�t�@�C�����̐擪�ɕt�^������t(YYYYMMDD)�ɑ����t�@�C�������w�肵�ĉ�����
$post_log_filename_suffix = 'log.csv';

# �������݃��O �Œ�o�͕�����
$bbs_pass = 'bbs1';

# �������݃��O �J�e�S�����ϊ��ݒ�
# �X���b�h�������Ɋ܂܂��J�e�S���L�[���[�h��
# �������݃��O�ɏo�͂���J�e�S�����̑Ή���ݒ肵�ĉ�����
#
# �ݒ��: @category_convert = ('test:�e�X�g');
#   ����: �X���b�h�^�C�g�������Ɂutest�v���܂ޏꍇ�A
#         �������݃��O�u�J�e�S���v���Ɂu�e�X�g�v�Əo�͂��A
#         �u�X���b�h���v���ɁA�X���b�h�^�C�g����������utest�v�������ďo�͂��܂�
@category_convert = (
);

# �������݃��O�̒u���L�^�@�\
# �������݃��O�̃��X���e��ɋL�^������e���ݒ�l�ɕ�����v����ꍇ�A
# ��v�����ϊ��O������ɑΉ�����ϊ��㕶������u;�v�ŋ�؂�A�������݃��O�ɋL�^���܂�
#
# �ݒ�l�́u'�ϊ��O:�ϊ���'�v�̏����Ŏw�肵�܂�
# �����w�肷��ꍇ�́A�u,�v�ŋ�؂�A�ݒ��̂悤�Ɏw�肵�܂�
#
# �ݒ��: @post_log_contents_replace = ('�ϊ��O1:�ϊ���1', '�ϊ��O2:�ϊ���2');
@post_log_contents_replace = (
);

#-------------------------------------------------
#  ���������ݗ����֘A�ݒ�
#-------------------------------------------------
# ����ID�Ǘ�WebProtect�Ƌ��L����ݒ�l�̃n�b�V���錾 (���̍��ڂ͐ݒ�s�v�ł�)
%history_shared_conf;

# ����ID�Ǘ�WebProtect�t�H���_�p�X
$history_webprotect_dir = './protect_rireki';

# ����ID�Ǘ�WebProtect ����ID���s�y�[�WURL
# �X���b�h�\�����(read.cgi)��
# �u����ID�������s�Ȃ̂ŋL�^����܂���B�y����ID�𔭍s����z�v�����N�̈ړ���URL
$history_webprotect_issue_url = "$history_webprotect_dir/index.cgi";

# ����ID�Ǘ�WebProtect��init.cgi��
# ����ID���s�`�Ԃ����[�U���� ($cf{pwd_regist} = 1;) �ɂ����ꍇ��
# ����ID���s������ʂ̖߂��yURL�p�X�z
# �� ���΃p�X�ɂĎw�肷��ꍇ�́A���̃t�@�C�����猩���p�X���w�肵�ĉ�����
$history_shared_conf{back_url} = "$history_webprotect_dir/index.cgi";

# ����ID���s�Ԋu�i�b�j
$history_shared_conf{wait_regist} = 60;

# ����ID���s�Ԋu���� ���O�z�X�g
@{$history_shared_conf{wait_regist_exempt_hosts}} = (
);

# �������ݗ����y�[�W�\��CGI�p�X
$historycgi = './history.cgi';

# �������ݗ������O�ۑ��t�H���_
$history_shared_conf{history_logdir} = './history';

# 1�̏������ݗ������O�t�H���_���̏������ݗ������O�t�@�C���ۑ���
# �������ݗ������O�t�@�C���𕡐��̃t�H���_�ɕ����ۑ�����ۂ�
# 1�̃t�H���_���ɕۑ����鏑�����ݗ������O�t�@�C������ݒ肵�܂�
$history_shared_conf{number_of_logfile_in_history_logdir} = 10000;

# �������ݗ������O�t�@�C�������ۑ� �t�H���_�ԍ����O�t�@�C��
# �������ݗ������O�t�@�C���𕪊��ۑ�����ۂ�
# �t�H���_�ԍ����L�^���郍�O�t�@�C���p�X��ݒ肵�܂�
# �� ���΃p�X�ɂĎw�肷��ꍇ�́A���̃t�@�C�����猩���p�X���w�肵�ĉ�����
$history_shared_conf{history_logdir_number} = './history_logdir_number.log';

# �������ݗ������O�t�@�C�������ۑ� �t�H���_�����O�t�@�C�����J�E���^�t�@�C��
# �ۑ��t�H���_���̏������ݗ������O�t�@�C�������L�^���郍�O�t�@�C���p�X��ݒ肵�܂�
# �� ���΃p�X�ɂĎw�肷��ꍇ�́A���̃t�@�C�����猩���p�X���w�肵�ĉ�����
$history_shared_conf{history_logfile_count} = './history_logfile_count.log';

# �������ݗ������O �����L�^�����
$history_save_max = 100;

# �������ݗ������O �L�^���O�X���b�h�^�C�g��
# �ʏ핶����̕�����v������s���A�X���b�h�^�C�g���Ƃ��̐ݒ�l�̂����ꂩ�����v�����ꍇ�A
# �������ݗ������O�ւ̋L�^���s���܂���
@history_save_exempt_titles = (
);

# �������ݗ����y�[�W 1�y�[�W������̃X���b�h�\����
$history_display_menu = 50;

#-------------------------------------------------
#  �������܂œǂ񂾋@�\
#-------------------------------------------------

# ����ǉ��������b�Z�[�W�́u�����v�����N��URL
$readup_to_here_added_history_link_url = $historycgi;

# ����ID��ێ����Ă��Ȃ��Ƃ��̃G���[���b�Z�[�W�����N��URL
$readup_to_here_not_login_error_link_url = 'http://hogehoge.com/';

#-------------------------------------------------
#  ���֎~���������̊O���t�@�C����
#-------------------------------------------------

# �֎~���������̊O���t�@�C���p�X
# �󗓂⑶�݂��Ȃ��t�@�C���p�X���w�肵�����́A�{�t�@�C���̐ݒ�l���g�p���܂�
# �yinit.cgi���猩���p�X���w�肵�ĉ������z
my $override_prohibit_settings_filepath = './prohibit-override.cgi';

#===========================================================
#  ���ݒ芮��
#===========================================================

# �摜�g���q
%imgex = (".jpg" => 1, ".gif" => 1, ".png" => 1);

# �ő�ŉ摜6���̃A�b�v���[�h
# �A�b�v���[�h�\���� ������Validate
$upl_increase_num = int($upl_increase_num);
if ($upl_increase_num > 3) {
	$upl_increase_num = 3;
} elsif ($upl_increase_num < 0) {
	$upl_increase_num = 0;
}

# NG���X�u���R�����g/�G���[���b�Z�[�W ������̃G�X�P�[�v
$ngres_comment =~ s/"{1}/\\"/g;
$ngid_error_message =~ s/"{1}/\\"/g;
$ngname_error_message =~ s/"{1}/\\"/g;

# Cookie�̃L�[���̈ꕔ�Ɏg�p����f�B���N�g���p�X�̎擾
$cookie_current_dirpath = do {
	my $dir_separator_regex = quotemeta(File::Spec->canonpath('/'));
	# �h�L�������g���[�g�x�[�X��CGI���s�p�X���擾���A�p�X���N���[���ɂ���
	my $tmp_dirpath = File::Spec->canonpath(dirname($ENV{'SCRIPT_NAME'}));
	$tmp_dirpath =~ s/(^${dir_separator_regex}?|${dir_separator_regex}?$)//g;
	# ���s�p�X��js�f�B���N�g���ȉ��̏ꍇ�ɂ�WebPatio���[�g�Ƃ���
	$tmp_dirpath =~ s/${dir_separator_regex}js(?:${dir_separator_regex}.*)?$//i;
	# URL�G���R�[�h
	$tmp_dirpath =~ s/(\W)/'%' . unpack('H2', $1)/eg;
	$tmp_dirpath =~ s/\s/+/g;
	$tmp_dirpath;
};

# ���������������reCAPTCHA�F�؃X�L�b�v Cookie�Í��� �閧��/���J�� �󔒍s����
$find_recaptcha_continue_cookie_rsa_private_key =~ s/^\s*//;
$find_recaptcha_continue_cookie_rsa_public_key =~ s/^\s*//;

# �X���b�h���O �ۑ��t�H���_�Ĕz�u���� ���b�N�t�@�C���p�X
$thread_log_moving_lock_path = "$logdir/moving_threadlog.lock";

# Encode���L�C���X�^���X�쐬
$enc_cp932 = Encode::find_encoding('cp932');

# �������ݗ������O �L�^���O�X���b�h�^�C�g�� �����G���R�[�h��
@history_save_exempt_titles = map { $enc_cp932->decode($_) } @history_save_exempt_titles;

#-------------------------------------------------
#  �A�N�Z�X����
#-------------------------------------------------
sub axscheck {
	# ���Ԏ擾
	my $localtime_ref;
	($time, $date, $localtime_ref) = &get_time;
	@localtime = @{$localtime_ref};

	# IP&�z�X�g�擾
	$host = $ENV{'REMOTE_HOST'};
	$addr = $ENV{'REMOTE_ADDR'};

	if ($gethostbyaddr && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}

	# UserAgent�擾
    ## _��-�ɒu�������A,:�������Ď擾
	($useragent = $ENV{'HTTP_USER_AGENT'}) =~ tr/_,:/-/d;
    ## �ݒ�l�ŁA�������̑������ɕ��ёւ����A���K�\���G�X�P�[�v�������X�g���擾
    my @ua_remove_strings_regex = map { quotemeta($_); } sort { length($b) <=> length($a) } grep { $_ ne '' } split(/,/, join(',', @useragent_remove_strings));
    if (scalar(@ua_remove_strings_regex) > 0) {
        # �}�b�`�p�^�[�����쐬���A�폜����
        my $match = '(?:' . join('|', @ua_remove_strings_regex) . ')';
        $useragent =~ s/$match//g;
    }

	# IP�`�F�b�N
	my $flg;
	foreach ( split(/\s+/, $deny_addr) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;

		if ($addr =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		&error("�A�N�Z�X��������Ă��܂���");

	# �z�X�g�`�F�b�N
	} elsif ($host) {

		foreach ( split(/\s+/, $deny_host) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			&error("�A�N�Z�X��������Ă��܂���");
		}
	}
	if ($host eq "") { $host = $addr; }

	## --- �������
	if ($authkey) {
		my $cookie_name = "patio_member_${cookie_current_dirpath}";

		# ���O�C��
		if ($mode eq "login") {

			# ������
			$my_name = "";
			$my_rank = "";

			# ����t�@�C���I�[�v��
			my $flg;
			open(IN,"$memfile") || &error("Open Error: $memfile");
			while (<IN>) {
				my ($id,$pw,$rank,$nam) = split(/<>/);

				if ($in{'id'} eq $id) {
					$flg = 1;

					# �ƍ�
					if (&decrypt($in{'pw'},$pw) == 1) {
						$flg = 2;
						$data = "$rank\t$nam";
						$my_name = $nam;
						$my_rank = $rank;
					}
					last;
				}
			}
			close(IN);

			# �ƍ��s��
			if ($flg < 2) { &error("�F�؂ł��܂���"); }

			# �Z�b�V����ID���s
			my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
			my $cookid;
			srand;
			foreach (1 .. 15) {
				$cookid .= $char[int(rand(@char))];
			}

			# �Z�b�V����ID���s
			open(OUT,"+> $sesdir/$cookid.cgi");
			print OUT "$in{'id'}\t$time\t$data";
			close(OUT);

			# �Z�b�V�����N�b�L�[���ߍ���
			print "Set-Cookie: $cookie_name=$cookid;\n";

			# �N�b�L�[ID�����O�C��ID
			$my_ckid = $cookid;
			$my_id   = $in{'id'};

		# ���O�C����
		} else {

			# �N�b�L�[�擾
			my $cook = $ENV{'HTTP_COOKIE'};

			# �Y��ID�����o��
			my %cook;
			foreach ( split(/;/, $cook) ) {
				my ($key,$val) = split(/=/);
				$key =~ s/\s//g;

				$cook{$key} = $val;
			}

			# �Z�b�V����ID�L�������`�F�b�N
			if ($cook{$cookie_name} !~ /^[a-zA-Z0-9]{15}$/ || !-e "$sesdir/$cook{$cookie_name}.cgi") {
				&enter_disp;
			}

			# �Z�b�V�����t�@�C���ǂݎ��
			open(IN,"$sesdir/$cook{$cookie_name}.cgi");
			my $ses_data = <IN>;
			close(IN);

			my ($id,$tim,$rank,$nam) = split(/\t/, $ses_data);

			# ���ԃ`�F�b�N
			if ($time - $tim > $authtime * 60) {

				unlink("$sesdir/$cook{$cookie_name}.cgi");
				print "Set-Cookie: $cookie_name=;\n";

				my $msg = qq|���O�C���L�����Ԃ��o�߂��܂����B�ēx���O�C�����Ă��������B<br>\n|;
				$msg .= qq|<a href="$bbscgi?mode=enter_disp">�y�ă��O�C���z</a>\n|;

				&error($msg);
			}

			# ���O���N�b�L�[ID�����O�C��ID
			$my_name = $nam;
			$my_ckid = $cook{$cookie_name};
			$my_id   = $id;
			$my_rank = $rank;
		}
	}
}

#-------------------------------------------------
#  �t�H�[���f�R�[�h
#-------------------------------------------------
sub parse_form {
	undef(%in);
	undef(%fname);
	undef(%uplno);
	undef(%ctype);
	$macbin = 0;
	$postflag = 0;

	# ��������name�ő����Ă����ꍇ�ɁA�Ō�̑��M�l���擾����name
	my @last_value_get_keys = ('save_history', 'increase_num');

	# �}���`�p�[�g�t�H�[���̂Ƃ�
	if ($image_upl && $ENV{'CONTENT_TYPE'} =~ m|multipart/form-data|i) {
		$postflag = 1;

		# �Y�t�t�@�C���ő吔
		my $max_upl_num = 3 + $upl_increase_num;

		# �ϐ�������
		local($bound,$key,$val);

		# �W�����͂��o�C�i�����[�h�錾
		binmode(STDIN);

		# �擪��boundary��F��
		$bound = <STDIN>;
		$bound =~ s/\r\n//;

		# �W�����͂�W�J
		while (<STDIN>) {

			# �}�b�N�o�C�i���F��
			if (m|application/x-macbinary|i) { $macbin = 1; }

			# Content-Disposition�F��
			if (/^Content-Disposition:/i) {
				$flg = 1;
			}

			# name�����F��
			if ($flg == 1 && /\s+name="([^";]+)"/i) {
				$key = $1;

				if ($key =~ /^upfile([1-$max_upl_num])$/) {
					$uplno = $1;
					$uplno{$uplno} = $uplno;
				}
			}

			# filename�����F���i�t�@�C���A�b�v�j
			if ($uplno && /\s+filename="([^";]+)"/i) {
				$fname{$uplno} = $1;
			}

			# Content-Type�F���i�t�@�C���A�b�v�j
			if ($uplno && /Content-Type:\s*([^";]+)/i) {
				my $ctype = $1;
				$ctype =~ s/\r//g;
				$ctype =~ s/\n//g;

				$ctype{$uplno} = $ctype;
			}

			# �w�b�_ �� �{��
			if ($flg == 1 && /^\r\n/) {
				$flg = 2;
				next;
			}
			# �{���F��
			if ($flg == 2) {
				# boundary���o �� �t�B�[���h�I��
				if (/^$bound/) {
					# �����̉��s���J�b�g
					$val =~ s/\r\n$//;

					# �e�L�X�g�n�͉��s��ϊ�
					if (!$uplno) {

						# S-JIS�R�[�h�ϊ�
						&jcode::convert(\$val, 'sjis');

						# �G�X�P�[�v
						$val =~ s/&/&amp;/g;
						$val =~ s/"/&quot;/g;
						$val =~ s/</&lt;/g;
						$val =~ s/>/&gt;/g;

						# �{�������NG���[�h�ENG�X���b�h���[�h�ݒ莞�ȊO�͉��s�R�[�h������
						if ($key ne "comment" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words') {
						$val =~ s/\r|\n//g;
						} 
						
						# �v���r���[�������NG���[�h�ENG�X���b�h���[�h�ݒ莞�͉��s��u�����Ȃ�
						if ($in{'mode'} ne "preview" && $in{'mode'} ne "resview" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words') {
#						} else {
#						if ($in{'mode'} eq "regist") {
						$val =~ s/\r\n/<br>/g;
						$val =~ s/\r/<br>/g;
						$val =~ s/\n/<br>/g;
						}
					}

					# �n�b�V����
					if (exists($in{$key}) && scalar(grep { $_ eq $key } @last_value_get_keys) > 0) {
						# ����name�����M����Ă����ꍇ�ɁA�Ō�̑��M�l���擾����name
						$in{$key} = $val;
					} else {
						$in{$key} .= "\0" if (defined($in{$key}));
						$in{$key} .= $val;
					}

					# �t���O��������
					$flg = $uplno = $key = $val = '';
					next;
				}
				# boundary���o�܂Ŗ{�����o���Ă���
				$val .= $_;
			}
		}

	# �}���`�p�[�g�t�H�[���ȊO�̂Ƃ�
	} else {

		my $buf;
		if ($ENV{'REQUEST_METHOD'} eq "POST") {
			$postflag = 1;
			read(STDIN, $buf, $ENV{'CONTENT_LENGTH'});
		} else {
			$buf = $ENV{'QUERY_STRING'};
		}
		foreach ( split(/&/, $buf) ) {
			my ($key, $val) = split(/=/);
			$val =~ tr/+/ /;
			$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

			# S-JIS�R�[�h�ϊ�
			&jcode::convert(\$val, 'sjis');

			# �G�X�P�[�v
			$val =~ s/&/&amp;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;

						# �{�������NG���[�h�ENG�X���b�h���[�h�ݒ莞�ȊO�͉��s�R�[�h������
						if ($key ne "comment" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words' && $in{'mode'} ne 'admin') {
						$val =~ s/\r|\n//g;

						} 

						# �v���r���[�������NG���[�h�ENG�X���b�h���[�h�ݒ莞�͉��s��u�����Ȃ�
						if ($in{'mode'} ne "preview" && $in{'mode'} ne "resview" && $key ne "ngwords" && $in{'mode'} ne 'ngthread_words' && $in{'mode'} ne 'admin')  {
			$val =~ s/\r\n/<br>/g;
			$val =~ s/\r/<br>/g;
			$val =~ s/\n/<br>/g;
			}
			
			# �n�b�V����
			if (exists($in{$key}) && scalar(grep { $_ eq $key } @last_value_get_keys) > 0) {
				# ����name�����M����Ă����ꍇ�ɁA�Ō�̑��M�l���擾����name
				$in{$key} = $val;
			} else {
				$in{$key} .= "\0" if (defined($in{$key}));
				$in{$key} .= $val;
			}
		}
	}
	$in{'sub'} .= $in{'add_sub'} if(defined($in{'add_sub'}));
	$mode = $in{'mode'};
	$p = $in{'p'};
	$i_nam = $in{'name'};
	$i_sub = $in{'sub'};
	$i_com = $in{'comment'};
	$headflag = 0;
	$l = $in{'l'};

	# �J�e�S���\���@�\ �J�e�S��������o���f�[�V����
	if ($in{'k'} ne '') {
		# ���p�p�������E����(1�`9)�ȊO���܂܂�Ă����ꍇ�A�@�\�𖳌��ɂ���
		if ($in{'k'} =~ /[^a-z1-9]/) {
			delete($in{'k'});
		} else {
			# �@�\���L���̏ꍇ�ɂ͐擪10������؂�o���A����ȍ~��؂�̂Ă�
			$in{'k'} = substr($in{'k'}, 0, 10);
		}
	}

	# �X���b�h���O �ۑ��t�H���_�Ĕz�u�������m
	# �Ĕz�u�������b�N�t�@�C�������݂���Ƃ��́A�������̉\�������邽��
	# �X���b�h���O�t�@�C���j���h�~�̂��߁A
	# �Ǘ���ʈȊO�̕\�����v�����ꂽ�ۂɁA�G���[�\�����s���܂�
	if (basename($ENV{SCRIPT_NAME}) ne basename($admincgi) && -e $thread_log_moving_lock_path) {
		error('�����e�i���X���ɂ��\���ł��܂���');
	}
}

#-------------------------------------------------
#  HTML�w�b�_
#-------------------------------------------------
sub header {
	my ($sub, $js, $disable_buffering) = @_;

	if ($sub ne '') { $title = $sub; }

	if ($disable_buffering) {
		# �W���o�͂̃I�[�g�t���b�V����L���� (�o�b�t�@�����O������)
		local $| = 1;
	}

	print "Content-type: text/html\n\n";

	if ($disable_buffering) {
		# �u���E�U�ł�256byte��M���Ȃ��ƃ����_�����O���J�n���Ȃ����߁A���p�X�y�[�X���o��
		for (my $i=0; $i<256; $i++) {
			print ' ';
		}
	}

	print <<"EOM";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
EOM
	if((caller 1)[3] =~ /^.*::find$/) { 
		print "<link rel=\"stylesheet\" href=\"https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css\">\n";
	}
	print <<"EOM";
<style type="text/css">
<!--
body,td,th { font-size:$b_size;	font-family:$b_face; }
a:hover { color:$al }
.num { font-size:12px; font-family:Verdana,Helvetica,Arial; }
.s1  { font-size:10px; font-family:Verdana,Helvetica,Arial; }
.s2  { font-size:10px; font-family:"$b_face"; }
a.ng_toggle:link    { text-decoration: none;      color: #00F; }
a.ng_toggle:visited { text-decoration: none;      color: #00F; }
a.ng_toggle:hover   { text-decoration: underline; color: #00F; }
a.ng_toggle:active  { text-decoration: none;      color: #00F; }
a.ng_toggle.enabled { color: #ff0002; }
.link_name2 { background-color:#ffe731; }
span.link_name1.ng_res, span.link_name2.ng_res { color: #a5a5a5; }
span[class^="hatugen_"].ngres_count { color: #a5a5a5; }
div.refRes { margin: 20px 0px 0px 20px; }
tbody#genkoulog { background-color: #ffff00; }
tbody#kakolog { background-color: #e2efda; ]
-->
</style>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
EOM

	# JavaScript
	if ($js eq "js") {
		print "<Script Language=\"JavaScript\">\n<!--\n";
		print "function MyFace(Smile) {\n";
		print "myComment = document.myFORM.comment.value;\n";
		print "document.myFORM.comment.value = myComment + Smile;\n";
		print "}\n//-->\n</script>\n";
	}

	# IE7�ȉ��ł�JSON���g�p�ł���悤�ɂ���
    print <<"EOM";
<!--[if lte IE 7]>
	<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/json3/3.3.2/json3.min.js"></script>
<![endif]-->
EOM

	# NGID/NG�l�[��/NG���[�h/�A��NG�@�\
    if((caller 1)[3] =~ /^.*::view$/) {
        # �ݒ�o��
        print "<script type=\"text/javascript\" src=\"js/config.min.js.cgi\"></script>\n";
        # NGID/NG�l�[��/NG���[�h/�A��NG�@�\
        # ��Q�ƃ��X�����\���E�W�J�\���@�\
        # print "<script type=\"text/javascript\" src=\"js/read.min.js\"></script>\n";
        print "<script type=\"text/javascript\" src=\"js/_original/read.js\"></script>\n";
		# �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\
		# �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\
		print "<script type=\"text/javascript\" src=\"js/read_prohibit.min.js\"></script>\n";
	}

	# �V�K�X���b�h�쐬�t�H�[���E���X�t�H�[���E���[�U�[�ԃ��[�����M�t�H�[���Ŏg�p����JavaScript�t�@�C��
	# �v���C�x�[�g�u���E�W���O���[�h����
	# �t�H�[�� submit�{�^������
	if ((caller 1)[3] =~ /^.*::(?:form|view|mailform)$/) {
		print "<script type=\"text/javascript\" src=\"js/pm.min.js\"></script>\n";
		print "<script type=\"text/javascript\" src=\"js/form.min.js\"></script>\n";
	}

	# �V�K�X���b�h�쐬�t�H�[���E���X�t�H�[��
	# �t�H�[�� �u3���ȏ�A�b�v���[�h����v����
	if ((caller 1)[3] =~ /^.*::(?:form|view)$/) {
		print "<script type=\"text/javascript\" src=\"js/upload.min.js\"></script>\n";
	}

	# ���[�h���� �������� �\����Ԑݒ�
	if((caller 1)[3] =~ /^.*::find$/) {
		print <<"EOM";
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1/i18n/jquery.ui.datepicker-ja.min.js"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js"></script>
<script type="text/javascript">
	// input type=date fallback
	\$(function() {
		if(!Modernizr.inputtypes.date) {
			\$('input[type=date]').datepicker({
				dateFormat: 'yy-mm-dd',
				beforeShow: function(input, inst) {
					setTimeout(function() {
						input = \$(input);
						inst.dpDiv.css({
							top: input.offset().top + input.height() + (inst.dpDiv.outerHeight() - inst.dpDiv.height()),
							left: input.offset().left
						});
					}, 0);
				}
			});
		}
	});

	// define find item block utility function
	var findItem = new (function() {
		// update display state
		this.updateDisplayState = function() {
			if(\$("input[name='type']").first().prop("checked")) {
				\$("#findItem").show();
			} else {
				\$("#findItem").hide();
			}
		}
		// add onLoad event
		\$(function() {
			// set onClick update event
			\$("input[name='type']").click(findItem.updateDisplayState);
			// update display state
			findItem.updateDisplayState();
		});
	})();
</script>
EOM
	}

	if((caller 1)[3] =~ /^.*::history_list_view$/) {
		print "<script type=\"text/javascript\" src=\"js/history.min.js\"></script>\n";
	}

	print "<title>$title</title></head>\n";

	# body�^�O
	if ($bg) {
		print qq|<body background="$bg" bgcolor="$bc" text="$tx" link="$lk" vlink="$vl" alink="$al">\n|;
	} else {
		print qq|<body bgcolor="$bc" text="$tx" link="$lk" vlink="$vl" alink="$al">\n|;
	}
	$headflag = 1;
}

#-------------------------------------------------
#  �����������b�Z�[�W
#-------------------------------------------------
sub success {
	my ($message, $back_url) = @_;

	chomp($back_url);
	if ($back_url eq '') {
		$back_url = 'history.back()';
	} else {
		$back_url = "location.href='$back_url'";
	}

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>SUCCESS</h3>
<p>$message</p>
<p>
<form>
<input type="button" value="�O��ʂɂ��ǂ�" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �G���[����
#-------------------------------------------------
sub error {
    my ($message, $back_url) = @_;

    chomp($back_url);
    if($back_url eq '') {
        $back_url = 'history.back()';
    } else {
        $back_url = "location.href='$back_url'";
    }

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>ERROR !</h3>
<p><font color="red">$message</font></p>
<p>
<form>
<input type="button" value="�O��ʂɂ��ǂ�" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

sub success {
	my ($message, $back_url) = @_;

	chomp($back_url);
	if($back_url eq '') {
		$back_url = 'history.back()';
	} else {
		$back_url = "location.href='$back_url'";
	}

	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<h3>SUCCESS !</h3>
<p><font>$message</font></p>
<p>
<form>
<input type="button" value="�O��ʂɂ��ǂ�" onclick="$back_url">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#check image type
sub check_imagetype {
	# checks file contents

	my ($data) = @_;
	if ($data =~ m[^\x89PNG]) {
		return q{image/x-png};
	}
	if (length $data > 1) {
		$substr = substr($data, 1, 1024);
		if (defined $substr && $substr =~ m[^PNG]) {
			return q{image/x-png};
		}
	}
	if (length $data > 0) {
		$substr = substr($data, 0, 2);
		if (pack('H*', 'ffd8') eq $substr) {
			return q{image/jpeg};
		}
	}
	if ($data =~ m[^GIF8]) {
		return q{image/gif};
	}

	if ($data =~ m[^hsi1]) {
		return q{image/x-jpeg-proprietary};
	}
}

#-------------------------------------------------
#  ���Ԏ擾
#-------------------------------------------------
sub get_time {
	$ENV{'TZ'} = "JST-9";
	my $time = time;
	my @localtime = localtime($time);
#	my ($min,$hour,$mday,$mon,$year) = (localtime($time))[1..5];
	my ($sec,$min,$hour,$mday,$mon,$year) = @localtime[0..5];

	# �����̃t�H�[�}�b�g
#	my $date = sprintf("%04d/%02d/%02d %02d:%02d", $year+1900,$mon+1,$mday,$hour,$min);
	my $date = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year+1900,$mon+1,$mday,$hour,$min,$sec);
	return ($time, $date, \@localtime);
}

#-------------------------------------------------
#  �������
#-------------------------------------------------
sub enter_disp {
	&header;
	print <<EOM;
<div align="center">
<table><tr><td>
�E �����ɂ̓��O�C��ID�ƃp�X���[�h���K�v�ł��B<br>
�E �u���E�U�̃N�b�L�[�͕K���L���ɂ��Ă��������B
</td></tr></table>
<form action="$bbscgi" method="post">
<input type="hidden" name="mode" value="login">
<Table border="0" cellspacing="0" cellpadding="0" width="200">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center">���O�C��ID</td>
  <td bgcolor="$col2" nowrap><input type="text" name="id" value="" size="20" style="width:160px"></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center">�p�X���[�h</td>
  <td bgcolor="$col2" nowrap><input type="password" name="pw" value="" size="20" style="width:160px"></td>
</tr>
</table>
</Td></Tr></Table>
<p></p>
<input type="submit" value="���O�C��" style="width:80px">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �X���b�h���O �ۑ��t�H���_�ԍ��擾
#-------------------------------------------------
sub get_logfolder_number {
	my ($thread_number) = @_;

	if ($number_in_threadlog_folder >= 1) {
		# $thread_number��1�n�܂�A�X���b�h���O�t�H���_��1�n�܂�
		# 5���Ƀ[���p�f�B���O����
		return sprintf('%05d', ((($thread_number - 1) / $number_in_threadlog_folder) + 1));
	} else {
		return;
	}
}

#-------------------------------------------------
#  �X���b�h���O �ۑ��t�H���_�p�X�擾
#-------------------------------------------------
sub get_logfolder_path {
	my ($thread_number) = @_;

	my $thread_logfolder_number = get_logfolder_number($thread_number);
	if (defined($thread_logfolder_number)) {
		return "$logdir/$thread_logfolder_number";
	} else {
		# 1������ݒ肵�Ă�ꍇ�́A�]����$logdir������Ԃ�
		return $logdir;
	}
}

#-------------------------------------------------
#  crypt�Í�
#-------------------------------------------------
sub encrypt {
	my ($inpw) = @_;

	# �������`
	my @char = ('a'..'z', 'A'..'Z', '0'..'9', '.', '/');

	# �����Ŏ�𐶐�
	srand;
	my $salt = $char[int(rand(@char))] . $char[int(rand(@char))];

	# �Í���
	crypt($inpw, $salt) || crypt ($inpw, '$1$' . $salt);
}

#-------------------------------------------------
#  crypt�ƍ�
#-------------------------------------------------
sub decrypt {
	my ($inpw, $enpw) = @_;

	if ($enpw eq "") { &error("�F�؂ł��܂���"); }

	# �픲���o��
	my $salt = $enpw =~ /^\$1\$(.*)\$/ && $1 || substr($enpw, 0, 2);

	# �ƍ�����
	if (crypt($inpw, $salt) eq $enpw || crypt($inpw, '$1$' . $salt) eq $enpw) {
		return 1;
	} else {
		return 0;
	}
}


#--------------#
#  ID��������  #
#--------------#

sub makeid {
	my $idnum = substr($addr, 8) ** 2;

	my @salt_charlist = ('.', 'A'..'Z', '/', 'a'..'z', 0..9);
	my $localtime = timegm(localtime($time)); # 0���ɐ؂�ւ��悤�AGMT����̎������܂߂ăG�|�b�N�o�ߕb���ɕϊ�����
	my $cycle_day = $localtime / 86400 % (scalar(@salt_charlist) ** 2); # salt�g�p�\����^salt2������1�T�C�N���Ƃ��āA�T�C�N�����̓������G�|�b�N����̓����̏�]�Ōv�Z
	my $salt = join('', @salt_charlist[int($cycle_day/scalar(@salt_charlist)), $cycle_day%scalar(@salt_charlist)]);

	$idcrypt = substr(crypt($idnum, $salt), -8);
}

#---------------------------------------
#  �g���b�v�@�\
#---------------------------------------
sub trip {
	my ($name) = @_;
	#���͂������O���̕����񂪂��̂܂܋L�^����܂��B
	return $name;
	$name =~ s/��/��/g;

	if ($name =~ /#/) {
		my ($handle,$trip) = split(/#/, $name, 2);

#		local($enc) = crypt($trip, $trip_key) || crypt ($trip, '$1$' . $trip_key);
#		$enc =~ s/^..//;

		# 2ch�݊��g���b�v
		my ($trip_key) = substr(substr($trip,0,8).'H.', 1, 2);
		$trip_key =~ s/[^\.-z]/\./go;
		$trip_key =~ tr/:;<=>?@[\\]^_`/ABCDEFGabcdef/;
		my ($enc) = substr(crypt($trip, $trip_key), -10);

		return "$handle��$enc";
	} else {
		return $name;
	}
}

#-------------------------------------------------
#  �N�b�L�[�擾
#-------------------------------------------------
sub get_cookie {
	# �Y��ID�����o��
	my %cook;
	foreach my $set (split(/;/, $ENV{'HTTP_COOKIE'})) {
		my ($key, $val) = split(/=/, $set);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# �f�[�^��URL�f�R�[�h���ĕ���
	my @cook;
	my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}";
	foreach my $val (split(/<>/, $cook{$cookie_name})) {
		$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		push(@cook, $val);
	}
	return @cook;
}

#-------------------------------------------------
#  Google AdSense
#-------------------------------------------------
sub googleadsense {

	if ($adsenseenable) {

# ������Google AdSense�̃R�[�h��\�邱�Ƃ��ł��܂��B
	print <<"EOM";
EOM

	}

}

#--------------------------#
#  �Ǘ���ʂł�init.cgi�ݒ�  #
#    �ϐ��I�[�o�[���C�h����     #
#--------------------------#
# �������̕ϐ�����default_�Ŏn�܂�ϐ���
# �Ǘ���ʓ�����ݒ��init.cgi��
# �ݒ�l���擾���邽�߂Ɏg�p���܂�
if($conf_override) {
	# �I�[�o�[���C�h�ݒ�t�@�C�������݂���Ƃ��͓ǂݍ���
	if(-f $conf_override_path) {
		require "$conf_override_path";
	}

	# �T���l�C���摜�T�C�Y
	$default_img_max_w = $img_max_w;
	$default_img_max_h = $img_max_h;
	if(defined $override_img_max_w && defined $override_img_max_h) {
		if($override_img_max_w =~ /^\d+$/ && $override_img_max_h =~ /^\d+$/) {
			$img_max_w = $override_img_max_w;
			$img_max_h = $override_img_max_h;
		}
	}

	# �T���l�C���摜�����T�C�Y
	$default_thumb_max_w = $thumb_max_w;
	$default_thumb_max_h = $thumb_max_h;
	if(defined $override_thumb_max_w && defined $override_thumb_max_h) {
		if($override_thumb_max_w =~ /^\d+$/ && $override_thumb_max_h =~ /^\d+$/) {
			$thumb_max_w = $override_thumb_max_w;
			$thumb_max_h = $override_thumb_max_h;
		}
	}

	# �A�b�v���[�h�\�t�@�C���g���q
	%default_imgex;
	while(my ($key,$value) = each(%imgex)) {
		$default_imgex{lc $key} = $value;
	}
	%imgex = %default_imgex;
	if(%override_imgex) {
		while(my ($key,$value) = each(%override_imgex)) {
			if($value =~ /[01]{1}/) {
				$imgex{lc $key} = $value;
			}
		}
	}
	my $enableExtCount = 0;
	$enableExtCount += $_ for values(%imgex);
	if($enableExtCount == 0) {
		# �A�b�v���[�h�\�t�@�C���g���q������Ȃ��Ƃ��́A�A�b�v���[�h�@�\���~
		$image_upl = 0;
	}
}

#-----------------------------------
#  �֎~���������̊O���t�@�C���ɂ��
#  �ϐ��I�[�o�[���C�h����
#-----------------------------------
if (defined($override_prohibit_settings_filepath) && -f $override_prohibit_settings_filepath) {
	# WebPatioProhibitOverrideConf�p�b�P�[�W���ŊO���t�@�C�����[�h
	package WebPatioProhibitOverrideConf;
	require "$override_prohibit_settings_filepath";

	# �w�肵�����O�̕ϐ��E�z��̂ݓǂݍ��݂��s��
	my @scalar_name_array = ('no_wd', 'ng_nm');
	my @array_name_array = (
		'duplicate_post_restrict_thread', 'hide_form_name_field', 'remove_name_on_post',
        'permit_name_regex', 'contents_branching_keyword', 'prohibit_img_md5hash',
		'firstpost_restrict_exempt',
		'disable_img_upload', 'disable_age', 'thread_browsing_restrict_user',
		'auto_post_prohibit_combination_imgmd5', 'auto_post_prohibit_multiple_submissions', 'auto_post_prohibit_old_thread_age'
	);
	for (my $i = 1; $i <= 20; $i++) {
		# �X���b�h�^�C�g�������������݋֎~�@�\�̃��X���������œ��삷��@�\
		# ���X���e �����P��ݒ�E�������O�P��ݒ�
		if ($i == 1) {
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_keyword");
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword");
		} else {
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_keyword_$i");
			push(@scalar_name_array, "auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_$i");
		}
	}
	foreach my $scalar_name (@scalar_name_array) {
		$main::{$scalar_name} = $WebPatioProhibitOverrideConf::{$scalar_name};
	}
	foreach my $array_name (@array_name_array) {
		@main::{$array_name} = @WebPatioProhibitOverrideConf::{$array_name};
	}

	# WebPatioProhibitOverrideConf�p�b�P�[�W���폜
	Symbol::delete_package('WebPatioProhibitOverrideConf');
}

# �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\
# �ݒ�l��z���
@auto_post_prohibit_thread_title_res_target_restrict_keyword_array = (
	$auto_post_prohibit_thread_title_res_target_restrict_keyword,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_2,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_3,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_4,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_5,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_6,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_7,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_8,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_9,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_10,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_11,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_12,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_13,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_14,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_15,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_16,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_17,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_18,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_19,
	$auto_post_prohibit_thread_title_res_target_restrict_keyword_20
);
@auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_array = (
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_2,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_3,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_4,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_5,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_6,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_7,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_8,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_9,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_10,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_11,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_12,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_13,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_14,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_15,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_16,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_17,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_18,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_19,
	$auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_20
);
@auto_post_prohibit_thread_title_res_target_hold_hour_array = (
	$auto_post_prohibit_thread_title_res_target_hold_hour_1,
	$auto_post_prohibit_thread_title_res_target_hold_hour_2,
	$auto_post_prohibit_thread_title_res_target_hold_hour_3,
	$auto_post_prohibit_thread_title_res_target_hold_hour_4,
	$auto_post_prohibit_thread_title_res_target_hold_hour_5,
	$auto_post_prohibit_thread_title_res_target_hold_hour_6
);

1;
