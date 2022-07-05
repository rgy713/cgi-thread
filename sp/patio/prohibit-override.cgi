#!/usr/bin/perl

#-------------------------------------#
# WebPatio �֎~�����㏑���ݒ�t�@�C�� #
#-------------------------------------#

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


# �֎~���[�h
# �� ���e���֎~���郏�[�h���R���}�ŋ�؂�
$no_wd = '';


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
# ���p�Ɨ����_�E�����_(ނ�����): \N{U+FF9E}\N{U+FF9F}
# �S�p�Ɨ����_�E�����_(�J����сK): \N{U+309B}\N{U+309C}
# ���p�X�y�[�X( ): \N{U+0020}
# �S�p�X�y�[�X(�@): \N{U+3000}
# ���p���Q��(!): \N{U+0021}
# �S�p���Q��(�I): \N{U+FF01}
# ���p��Ǔ_(�����ѡ): \N{U+FF64}\N{U+FF61}
# �S�p��Ǔ_(�A����сB): \N{U+3001}\N{U+3002}
# ���p���_(�): \N{U+FF65}
# �S�p���_(�E): \N{U+30FB}
# ���p����(�): \N{U+FF70}
# �S�p����(�[): \N{U+30FC}
# �n�C�t���}�C�i�X(-): \\\N{U+002D}
# ���p�v���X(+): \N{U+002B}
# �S�p�v���X(�{): \N{U+FF0B}
# ���p�s���I�h(.): \N{U+002E}
# �S�p�s���I�h(�D): \N{U+FF0E}
# ���p����(=): \N{U+003D}
# �S�p����(��): \N{U+FF1D}
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
    "\N{U+FF1D}" # �S�p����
);


#-------------------------------------------------
#  ���\�����e����@�\
#-------------------------------------------------
# �X���b�h�y�[�W�ŕ\���͈͂̃��X�ɐݒ肵����������܂ނ��A
# �摜�A�b�v�`�F�b�N���L���iinit.cgi�Őݒ�j�̏ꍇ�͉摜���܂܂�Ă���ꍇ�ɁA
# �\�����e��ύX���ďo�͂��܂�

# �\�����e����@�\ �Ώە�����ݒ�
@contents_branching_keyword = ();


#-------------------------------------------------
#  ���A�b�v���[�h�֎~�摜�w��@�\
#-------------------------------------------------

# �A�b�v���[�h�֎~�摜�t�@�C�� MD5�n�b�V���l�ݒ�
# �֎~�摜�Ƃ��Č��m����A�I���W�i���摜�t�@�C����MD5�n�b�V���l��ݒ肵�܂�
# ���͗�: 'd41d8cd98f00b204e9800998ecf8427e',
@prohibit_img_md5hash = (
);


#-------------------------------------------------
#  �����񏑂����݂܂ł̎��Ԑ����@�\
#-------------------------------------------------
# ���񏑂����݂܂ł̎��Ԑ����@�\ �ΏۊO���[�U�[�ݒ�
# �����Ώۂ��珜�O���郆�[�U�[��
# �u�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID�v�̂悤�Ɏw�肵�܂�
@firstpost_restrict_exempt = (
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
#  ���X���b�h�{�������@�\ �ݒ荀��
#-------------------------------------------------

# �X���b�h�{�������Ώۃ��[�U�[
# '����:�X���b�h��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:CookieA�̗L��:���t�ɂ�鏜�O:CookieA or �o�^ID or ����ID�̏��O:������' �̃��X�g�Őݒ肵�܂�
# (�擪�́u�����v�̃t�B�[���h�� �� ���Z�b�g����Ă���ݒ�́A�����Ώ۔�����s���܂���)
@thread_browsing_restrict_user = (
);

#-------------------------------------------------
#  �������������݋֎~�@�\
#-------------------------------------------------

# �X���b�h�^�C�g��(�ے����)�E�ϊ��O/�ϊ���摜��MD5�E��v�����O�o�̓R�����g�E�z�X�g����UserAgent�ECookieA or �o�^ID or ����ID�̑g�ݍ��킹
@auto_post_prohibit_combination_imgmd5 = (
);

## �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\ ##

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

# �����񓊍e���̎����������݋֎~�@�\ �����Ώېݒ�
# �u����:�X���b�h��:���X1�̏��O�P��:�����P��:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:���Ԏw��:�������v�̂悤�Ɏw�肵�܂�
# �X���b�h���E�z�X�g��UserAgent�̑g�ݍ��킹�̎w��ł́A�擪�u!�v�ɂ��ے�����̗��p���\�ł�
@auto_post_prohibit_multiple_submissions = (
);

# �ÃX��age�̎����������݋֎~�@�\ �����Ώېݒ�
# �u����:�X���b�h��:���O���X�������ԑO:�z�X�g<>UserAgent:CookieA or �o�^ID or ����ID:�v���C�x�[�g���[�h:���Ԏw��:�������v�̂悤�Ɏw�肵�܂�
# �X���b�h���E�z�X�g��UserAgent�̑g�ݍ��킹�̎w��ł́A�擪�u!�v�ɂ��ے�����̗��p���\�ł�
@auto_post_prohibit_old_thread_age = (
);

# �ȉ��̍s�͍폜���Ȃ��ŉ�����
1;
