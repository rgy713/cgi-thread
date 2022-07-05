#!/usr/bin/perl

#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� regist.cgi - 2011/07/06
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���肵�܎� K1.10
# 2014/08/10 �X���b�h�̘A���쐬�A���X�̘A�����e�̏������[�`���̕ύX
# 2013/03/03 �ߋ����O�̃o�O�C��
# 2012/09/08 �ߋ����O�̃o�O�C��
# 2011/07/06 3.4�����ɏC��
# 2010/06/23 �V�K�X���b�h�쐬�ƃ��X�̃^�C�}�[�𕪂��Ă݂܂���
# 2010/01/11 �֎~���[�h�Ɉ������������L�[���[�h�����|�[�g����悤��
# 2009/07/06 sub delete�͎g���ĂȂ��͗l�Ȃ̂Ń\�[�X�R�[�h���폜
#            �L���̍폜���Ƀ��X�̐����J�E���g�������悤�ɕύX
# 2009/06/23 �L���{����ʂ̃X�p�i����������Ƃ��ɐe�L���𕪊��i�R�s�[�j�ł��Ȃ������o�O�̏C��
# 2009/06/15 ���X�����v�Z���Ă��镔���Ő���������@��ɂ͐��������悤�ɏC��
# 2009/06/01 ���[�U�[�ԃ��[���@�\�𖳌��ɂł���悤��
# 2009/05/18 ���[�����M�@�\�̍T���ō��o�l����������o�O�̏C��
# 2009/03/28 FAQ���[�h
# 2009/03/14 �X���b�h�쐬�������[�h�̒ǉ�
# 2009/01/12 �֎~��t�B���^��URL�����K�p
# 2008/12/22 3.22�����ɏC��
# 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V
# 2008/04/28 �X���b�h�̍Ō�̋L�����폜����ƍŏI�A�N�Z�X���Ԃ��폜�����L���̎��ԂɂȂ��Ă��܂��o�O�̏C��
# 2008/02/27 �X���b�h�����@�\�𑕔��i�����ɂ͎w�背�X�ȍ~���R�s�[���ĐV�K�X���b�h�쐬�j
# 2008/01/15 ���X���m�点���[���̃��[�`���g�ݍ���
# 2008/01/09 �ߋ����O�ɗ����ĂĂ��������݂��ł���Z�L�����e�B��̖��ɑΏ�
# 2007/06/25 ���X���폜���ă��X����0�ɂȂ�Ƃ��ɁA���X�^�C�g�����e�L���̃^�C�g���ɂȂ�̂��C��
# 2007/06/10 3.2�����ɏC��
# 2007/05/01 ���[�U�[�̋L���폜���Ƀ��X�������B���X��0�ɂȂ�Ƃ��̕\���C��
# 2007/04/06 �X���b�h�g�b�v�̋L������A�Ǘ��҃p�X�Œ��ڃX���b�h�폜���ł���t�H�[����ݒu
# 2007/03/06 2ch�݊��g���b�v

# �O���t�@�C����荞��
BEGIN {
	require './init.cgi';
	require $jcode;
	eval "use lib '$webprotect_path/lib'";
	eval 'use WebProtectAuth';
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use HTML::Entities qw();
use ThreadUpdateLogDB;
use LWP::UserAgent;
use JSON::XS;
use URI;
use File::Spec;
use POSIX qw/strftime/;
use UniqueCookie;
use List::MoreUtils;
use HistoryCookie;
use HistoryLog;
use FirstCookie;
use MIME::Base64;
use AutoPostProhibit;
use ThreadCreatePostRestrict;
use Matcher::Utils;
use Matcher::Variable;
no encoding;

&parse_form;
&axscheck;

# Matcher::Utils �C���X�^���X������
# ($mode �� "regist" �������� "mailsend" �̂Ƃ��̂ݏ���������)
# (������ Matcher::Variable �C���X�^���X�����������ăZ�b�g)
my Matcher::Utils $mu;
if ($mode eq "regist" || $mode eq "mail") {
	$mu = Matcher::Utils->new(
		$time,
		$enc_cp932,
		$match_hiragana_katakana_normalize_mode,
		Matcher::Variable->new($match_variable_settings_filepath),
		\&trip,
		$restrict_user_from_thread_page_target_log_path,
		$restrict_user_from_thread_page_target_hold_hour_1,
		$restrict_user_from_thread_page_target_hold_hour_2,
		$restrict_user_from_thread_page_target_hold_hour_3,
		$restrict_user_from_thread_page_target_hold_hour_4,
		$restrict_user_from_thread_page_target_hold_hour_5,
		$restrict_user_from_thread_page_target_hold_hour_6,
		$restrict_user_from_thread_page_target_hold_hour_7,
		$restrict_user_from_thread_page_by_time_range_target_log_path,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_1,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_2,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_3,
		$restrict_user_from_thread_page_by_time_range_target_hold_hour_4,
		$restrict_user_from_thread_page_by_time_range_enable_time_range,
		$in_thread_only_restrict_user_from_thread_page_target_log_path,
		$in_thread_only_restrict_user_from_thread_page_target_hold_hour
	);
}

if ($mode eq "regist") { &regist; }
elsif ($mode eq "del") { &delete; }
elsif ($mode eq "mente") { &mente; }
elsif ($mode eq "edit_log") {
	require $editlog;
	&edit_log;
}
elsif ($mode eq "mail") { &mailsend; }
&error("�s���ȏ����ł�");

#-------------------------------------------------
#  �L�����e����
#-------------------------------------------------
sub regist {
	local (%fn, %ex, %image_orig_md5, %image_conv_md5);

	#�u�X���b�h�𐶐��v���N���b�N���A�u�m�F�v�Ƀ`�F�b�N�������Ă��Ȃ��ꍇ�̓G���[��ʂ�\�����܂��B
	# �v���r���[�@�\��L���i$restitle = 0;�j�ɂ����ꍇ�́A�`�F�b�N�{�b�N�X��\�����܂���B
	if ($restitle && $in{'res'} eq ''){
		if( $in{'confirm'} ne 'on') {
			error("�m�F���`�F�b�N���ĉ������B");
		}
	}

	# �����`�F�b�N
	if ($authkey && $my_rank < 2) {
		&error("���e�̌���������܂���$my_rank");
	}

	# POST����
	if ($postonly && !$postflag) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �����`�F�b�N
	$in{'res'} =~ s/\D//g;

	# ���s�X���b�hindex�t�@�C���I�[�v��
	open(my $nowfile_fh, '+<', $nowfile) || &error("Open Error: $nowfile");
	flock($nowfile_fh, 2) || error("Lock Error: $nowfile");

	# �����������݋֎~�@�\�̏��O��URL���̂��߂́A�V�K�X���b�h �X���b�hNo�̔�
	my $new;
	{
		my $top = <$nowfile_fh>;
		my ($no) = split(/<>/, $top);
		$new = $no + 1; # �V�K�쐬�� �X���b�h�ԍ��̔�
		seek($nowfile_fh, 0, 0); # �t�@�C���|�C���^��߂�
	}

	# �t�H�[�����瑗�M���ꂽ�v���C�x�[�g�u���E�W���O���[�h�ł��邩�ǂ����̏����擾
	my $is_private_browsing_mode = (exists($in{'pm'}) && $in{'pm'} eq '1') ? 1 : 0;

	# ���j�[�NCookieA�C���X�^���X���쐬
	my $cookie_a = UniqueCookie->new($cookie_current_dirpath);

	# Cookie�ɕۑ�����Ă���o�^ID���擾
	my $user_id_on_cookie = do {
		my @cookies = get_cookie();
		$cookies[5] || '';
	};

	# ����ID���擾
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};

	# �ԐM���X�̓��O�L�^�ȊO�X���b�h�^�C�g�����^�C�g���Ƃ���
	my $log_fh;
	my %first_res;
	my $file = '';
	my @log;
	my $newno = 0;
	if ($in{'res'} ne '') {
		# �t�@�C���I�[�v��
		# (���̉ӏ��ł��t�@�C���n���h���g�p���邽�߁A�r�����b�N���ăI�[�v�������܂܂Ƃ���)
		my $logfile_path = get_logfolder_path($in{'res'}) . "/$in{'res'}.cgi";
		open($log_fh, '+<', $logfile_path) || error("Open Error: $in{'res'}.cgi");
		flock($log_fh, 2) || error("Lock Error: $in{'res'}.cgi");
		seek($log_fh, 0, 0);

		# �X���b�h���O�ǂݍ���
		my $loaded_lines = 0;
		while (my $log_line = <$log_fh>) {
			# �������ݎ��̂��߂ɁA�����O�f�[�^��ۊ� (�w�b�_�[�s������)
			if ($loaded_lines > 0) {
				$file .= $log_line;
			}
			chomp($log_line);
			my @res_log = split(/<>/, $log_line);
			if ($loaded_lines == 0) {
				# �X���b�h�^�C�g���擾
				$i_sub = $res_log[1];

				# ���X�ԍ��̔�
				my $res = $res_log[2];
				if ($res == 0) {
					$newno = 2;
				} else {
					$newno = $res + 1;
				}
			} elsif ($loaded_lines == 1) {
				# >>1�̎擾
				# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\�̃X���b�h�쐬�҂̏��O�@�\
				# >>1�� �z�X�g, URL��, �o�^ID, CookieA, ����ID ���擾
				(my $valid_history_id = $res_log[20]) =~ s/\@$//;
				%first_res = (
					'host'       => $res_log[6],
					'url'        => $res_log[8],
					'user_id'    => $res_log[16],
					'cookie_a'   => $res_log[18],
					'history_id' => $valid_history_id,
				);
			}
			# ���O�z��ɒǉ�
			push(@log, \@res_log);
			$loaded_lines++;
		}

		# �t�@�C���|�C���^��擪�ɖ߂�
		seek($log_fh, 0, 0);
	}

	# �X���b�h�^�C�g������p�ϐ�(�J�e�S����������)
	my $check_i_sub = $i_sub;
	if (defined($in{'add_sub'})) {
		$check_i_sub =~ s/\Q${in{'add_sub'}}\E$//;
	}

	# ����Cookie�C���X�^���X������
	my $first_cookie = FirstCookie->new(
		$mu,
		$firstpost_restrict_settings_filepath,
		$time, $host, $useragent, $cookie_a, $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
		$cookie_current_dirpath, \@firstpost_restrict_exempt
	);

	# ���񏑂����݂܂ł̎��Ԑ����@�\
	{
		# ����
		my $type = $in{'res'} eq '' ? FirstCookie::THREAD_CREATE : FirstCookie::RESPONSE;
		$first_cookie->judge_and_update_cookie($type, $check_i_sub);

		# �������Ԏ擾
		my $left_hours = $first_cookie->get_left_hours_of_restriction();
		if ($left_hours > 0) {
			my $post_type = $in{'res'} eq '' ? '�X���b�h�쐬' : '���X';
			my $restrict_hours = $first_cookie->get_hours_of_restriction();
			my $back_url = $ENV{'HTTP_REFERER'} || ($in{'res'} eq '' ? "$readcgi?mode=form" : "$readcgi?no=$in{'res'}");
			error("${post_type}���\\�ɂȂ�܂ł���${left_hours}���Ԃł��B��${restrict_hours}", $back_url);
		}
	}

	# ���O����\���@�\ (�ԐM���X���̂�)
	my $is_hide_name_field_in_form = $in{'res'} ne '' && $mu->is_hide_name_field_in_form($check_i_sub, \@hide_form_name_field);
	if ($is_hide_name_field_in_form) {
		# �ΏۃX���b�h�̏ꍇ�́A�����Ă����l�ɂ�����炸�A���O����l�Ƃ���
		$i_nam = '';
	}

	# �`�F�b�N
	if ($no_wd) { &no_wd; }
	if ($jp_wd) { &jp_wd; }
	if ($urlnum > 0) { &urlnum; }

	# �R�����g�������`�F�b�N
	if (length($i_com) > $max_msg*2) {
		&error("�������I�[�o�[�ł��B<br>�S�p$max_msg�����ȓ��ŋL�q���Ă�������");
	}

	# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �C���X�^���X������
	my $thread_create_post_restrict = ThreadCreatePostRestrict->new(
		$mu,
		$thread_create_post_restrict_settings_filepath,
		$host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
		$cookie_a
	);

	# �X���b�h�쐬�����@�\
	if ($in{'res'} eq '' ) {
		# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �X���b�h�쐬�����@�\ ������Ԏ擾
		my $thread_create_restrict_status = $thread_create_post_restrict->determine_thread_create_restrict_status();

		if ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
		) {
			error('�X���b�h�쐬���ł��܂���B');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_2) {
			error('�X���b�h�쐬���ł��܂���B');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_3) {
			error('�X���b�h�̍쐬�͏o���܂���B����');
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_4) {
			error('�X���b�h�̍쐬�͏o���܂���B����');
		} elsif (!$webprotect_auth_new
			&& $thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_5) {
			# �����I��WebProtect�ɂ��o�^ID�F�؂��s�킹��
			$webprotect_auth_new = 1;
		}
	}

	# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\(���X���e��)
	if ($in{'res'} ne '') {
		# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\ ������Ԏ擾
		my $post_restrict_status = $thread_create_post_restrict->determine_post_restrict_status_by_thread_title(
			$check_i_sub, $first_res{'host'}, $first_res{'url'}, $first_res{'user_id'}, $first_res{'cookie_a'}, $first_res{'history_id'}
		);

		my $msg;
		if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
			|| $mu->is_in_thread_only_restricted_user_from_thread_page($in{'res'}, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
		) {
			# �����Ώۂ̏ꍇ�̓G���[���b�Z�[�W���`����
			$msg = '�������݂��ł��܂���B';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2) {
			# �����Ώۂ̏ꍇ�̓G���[���b�Z�[�W���`����
			$msg = '�������݂��ł��܂���B';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3) {
			$msg = '���̃X���b�h�ւ̏������݂͏o���܂���B����';
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4) {
			$msg = '���̃X���b�h�ւ̏������݂͏o���܂���B����';
		} elsif (!$webprotect_auth_res
			&& $post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5) {
			# �o�^ID�F�؂��������̂ݔ���
			# �����Ώۂ̏ꍇ��WebProtect�F�؂�L���ɂ���
			$webprotect_auth_res = 1;
		}
		if (defined($msg) && !($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION)) {
			# �X���b�h�쐬�҈ȊO���A
			# >>1��URL����jogai�Ǝw�肳��Ă��Ȃ��ꍇ(�X���b�h�쐬�҂̏��O�@�\�̑ΏۊO)�́A
			# �G���[���b�Z�[�W��\��
			error($msg);
		}
	}

	# WebProtect�o�^ID�F�؋@�\ �ݒ�󋵎擾
	my $webprotect_auth = $in{'res'} eq "" ? $webprotect_auth_new : $webprotect_auth_res;

	# �A�b�v���[�h�t�@�C�����ݔ���
	my $upfile_exists = $image_upl && grep { $in{'upfile' . $_} } (1 .. ($in{'increase_num'} ? 3 + $upl_increase_num : 3));

	# �z�X�g�Ȃǂɂ��摜�A�b�v���[�h�̖���
	$upfile_exists &&= !$mu->is_disable_upload_img($check_i_sub, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode, \@disable_img_upload);

	# ���e���e�`�F�b�N
	if ($i_nam eq "") {
		if ($in_name) { &error("���O�͋L���K�{�ł�"); }
		else { $i_nam = '������'; }
	}
	if ($in_mail == 1 && $in{'email'} ne "") { &error("E-mail�͓��͋֎~�ł�"); }
	if ($in_mail == 2 && $in{'email'} ne "") { &error("E-mail�͓��͋֎~�ł�"); }
	if ($in_mail == 3 && $in{'email'} ne "") { &error("E-mail�͓��͋֎~�ł�"); }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		&error("E-mail�̓��͓��e���s���ł�");
	}
	if ($in_url == 1 && $in{'url'} eq "") { &error("URL��K�����͂��Ă�������"); }
	if ($in_url == 1 && $in{'url'} eq "http://") { &error("URL��K�����͂��Ă�������"); }
	if ($in_url == 2 && $in{'url'} ne "") { &error("URL��񂪕s���ł�"); }
	if ($in_url == 3 && $in{'url'} ne "") { &error("URL���ɉ������͂��Ă͂����܂���"); }
	if ($check_i_sub eq "") { &error("�^�C�g���͋L���K�{�ł�"); }
	if ($check_i_sub =~ /^(\x81\x40|\s)+$/) { &error("�^�C�g���͐������L�����Ă�������"); }
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { &error("���O�͐������L�����Ă�������"); }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { &error("�R�����g�͐������L�����Ă�������"); }
	if ($in_pwd && $in{'pwd'} eq "") { &error("�p�X���[�h�͓��͕K�{�ł�"); }
	if (length($in{'pwd'}) > 8) { &error("�p�X���[�h��8�����ȓ��ɂ��ĉ�����"); }
	if ($webprotect_auth && $in{'user_id'} eq "") { &error("�o�^ID�͓��͕K�{�ł�"); }
	if ($webprotect_auth && $in{'user_pwd'} eq "") { &error("�o�^�p�X���[�h�͓��͕K�{�ł�"); }
	if ($in{'url'} eq "http://") { $in{'url'} = ""; }
	elsif ($in{url} && $in{url} !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/) {
		&error("URL��񂪕s���ł�");
	}

	# ���O����NG���[�h����
	ng_nm();

	# ID���쐬
	if($idkey) { &makeid; }
	else { $idcrypt = "";}

	# �t�@�C���A�b�v
	local($upl_flg, %w ,%h, %thumb_w, %thumb_h);
	my $upfile_count = 0; # �t�@�C���A�b�v��
	if ($upfile_exists) {
		require $upload;
		($fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1},
			$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2},
			$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3},
			$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4},
			$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5},
			$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}) = &upload($time, $in{'increase_num'});

		# �t�@�C���A�b�v���J�E���g
		$upfile_count = scalar(grep { defined($_) && $_ ne '' } values(%ex));

		# �摜�A�b�v�̂Ƃ��̓t���O�𗧂Ă�
		if ($upfile_count > 0) { $upl_flg = $time; }
	}

	# �t�@�C���A�b�v������A�{�����Ȃ��ꍇ�ɃG���[�\��
	if ($i_com eq "" && $upfile_count == 0) {
		error("�R�����g�̓��e������܂���");
	}

	# �A�����e������r�Ώۂ͓o�^ID�ł��邩�ǂ���
	my $user_id_is_post_limit_comparision_item = ($webprotect_auth && $in{'user_id'}) ? 1 : 0;

	# �A�����e������r�Ώۂ�����
	my $postLimitComparisonFirstItem = $user_id_is_post_limit_comparision_item ? $in{'user_id'} : $host;

	# �V�K���e�L�^�t�@�C���I�[�v�� (�V�K�X���b�h�쐬���̂�)
	# �z�X�g�Ȃǂɂ��X���b�h�쐬�}���@�\�Ŏg�p���邽�߁A��ɃI�[�v��
	my $threadlog_fh;
	my @threadlog_tmp;
	my $threadlog_same_user_found_for_suppress_thread_creation;
	my $add_to_threadlog;
	if ($in{'res'} eq '') {
		open($threadlog_fh, '+<', $threadlog) || &error("Open Error: $threadlog");
		flock($threadlog_fh, 2) || &error("Lock Error: $threadlog");
		seek($threadlog_fh, 0, 0);

		# �A�����eIP/�o�^ID�`�F�b�N (�t�@�C���n���h���N���[�Y�́u�V�K���e���O�֋L�^�v�̌�ɍs��)
		my $is_same_user;
		while (<$threadlog_fh>) {
			chomp($_);
			if ($_ eq '') {
				next;
			}
			my ($record_host, $record_cookie_a, $record_user_id, $record_history_id, $post_time) = split(/<>/, $_);
			my $passed_wait_thread = $wait_thread < $time - $post_time; # ���̃��O�s��$wait_thread�b�o�߂��Ă��邩�ǂ���
			# ���ꃆ�[�U�[����
			$is_same_user ||=
				!$passed_wait_thread
				&& (
					(!$user_id_is_post_limit_comparision_item && $record_host eq $host)
					|| ($record_cookie_a ne '-' && $record_cookie_a eq $cookie_a->value())
					|| ($user_id_is_post_limit_comparision_item && $record_user_id ne '-' && $record_user_id eq $in{'user_id'})
					|| ($record_history_id ne '-' && $record_history_id eq $chistory_id)
				);
			# �z�X�g�Ȃǂɂ��X���b�h�쐬�}���@�\�̂��߂̓��ꃆ�[�U�[����
			$threadlog_same_user_found_for_suppress_thread_creation ||=
				!$passed_wait_thread
				&& (
					$record_host eq $host
					|| ($record_cookie_a ne '-' && $record_cookie_a eq $cookie_a->value())
					|| ($record_user_id ne '-' && $record_user_id eq $user_id_on_cookie)
					|| ($record_history_id ne '-' && $record_history_id eq $chistory_id)
				);
			if ($is_same_user || $passed_wait_thread) {
				# ���ꃆ�[�U�[���A$wait_thread�o�߂������O�s�̓X�L�b�v
				next;
			}
			# �c�����O�s���L�^�z��ɒǉ�
			push(@threadlog_tmp, $_);
		}
		if ($is_same_user) {
			# ���ꃆ�[�U�[�ŁA$wait_thread���o�߂��Ă��Ȃ����O�s�������������ɃG���[�\��
			close($threadlog_fh);
			&error("�A�����e�͂������΂炭���Ԃ������ĉ�����");
		}

		# �V�K���e�L�^�t�@�C���ǋL�T�u���[�`����`
		$add_to_threadlog = sub {
			# �V�K�X���b�h�̓��e���O��z��̐擪�ɒǉ�
			my @add_new_thread_log = (
				$host,
				defined($cookie_a->value()) ? $cookie_a->value() : '-',
				exists($in{'user_id'}) && $in{'user_id'} ne '' ? $in{'user_id'} : '-',
				defined($chistory_id) ? $chistory_id : '-',
				$time,
				'' # �Ō��<>�����邽�߂�dummy�v�f
			);
			unshift(@threadlog_tmp, join('<>', @add_new_thread_log));

			# $hostnum�ȏ�̐V�K�X���b�h�쐬���O�����݂���ꍇ�A�������폜
			my $threadlog_excess_elements_count = scalar(@threadlog_tmp) - $hostnum;
			if ($threadlog_excess_elements_count > 0) {
				splice(@threadlog_tmp, $hostnum, $threadlog_excess_elements_count);
			}
			seek($threadlog_fh, 0, 0);
			print $threadlog_fh join("\n", @threadlog_tmp)."\n";
			truncate($threadlog_fh, tell($threadlog_fh));
			close($threadlog_fh);
		};
	}

	# ���j�[�NCookieA��K�v�ɉ����Ĕ��s
	my $is_cookie_a_issuing = !$cookie_a->is_issued();
	$cookie_a->value(1);

	# �����������݋֎~�@�\
	# �z�X�g�Ȃǂɂ��X���b�h�쐬�}���@�\
	# ������{
	{
		# AutoPostProhibit �C���X�^���X������
		my $auto_post_prohibit_instance = AutoPostProhibit->new(
			$mu,
			$prohibit_suppress_settings_filepath, $auto_post_prohibit_log_path, $auto_post_prohibit_no_delete_log_path, $auto_post_prohibit_thread_number_res_target_log_path, $auto_post_prohibit_thread_title_res_target_log_path,
			$auto_post_prohibit_multiple_submissions_count_log_path, $auto_post_prohibit_old_thread_age_count_log_path,
			\@category_convert, $auto_post_prohibit_log_concat_url[0],
			$auto_post_prohibit_exempting_name, \@auto_post_prohibit_additional_match_required_host, $auto_post_prohibit_delete_time, \@auto_post_prohibit_up_to_res_number,
			$auto_post_prohibit_thread_number_res_target_hold_hour_1, $auto_post_prohibit_thread_number_res_target_hold_hour_2, $auto_post_prohibit_thread_number_res_target_hold_hour_3,
			$auto_post_prohibit_thread_number_res_target_hold_hour_4, $auto_post_prohibit_thread_number_res_target_hold_hour_5, $auto_post_prohibit_thread_number_res_target_hold_hour_6,
			\@auto_post_prohibit_thread_title_res_target_restrict_keyword_array, \@auto_post_prohibit_thread_title_res_target_restrict_exempt_keyword_array, \@auto_post_prohibit_thread_title_res_target_hold_hour_array,
			\@auto_post_prohibit_combination_imgmd5,
			\@auto_post_prohibit_multiple_submissions, $auto_post_prohibit_multiple_submissions_redirect_threshold, $auto_post_prohibit_multiple_submissions_log_hold_minutes,
			\@ngthread_thread_list_creator_name_override_exclude_hosts,
			\@auto_post_prohibit_old_thread_age, $auto_post_prohibit_old_thread_age_redirect_threshold, $auto_post_prohibit_old_thread_age_log_hold_minutes,
			\@ngthread_thread_list_creator_name_override_exclude_hosts,
			$time, $date, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode,
			$cookie_a, $is_cookie_a_issuing
		);

		# ����g�p����
		my $new_thread_flag = $in{'res'} eq '';
		my $thread_no = $in{'res'} eq '' ? $new : int($in{'res'});
		my $age_flag = $in{'sage'} ne '1';
		my $name = $enc_cp932->decode(trip($i_nam)); # �g���b�v������̖��O�Ŕ���
		my $title = $enc_cp932->decode($i_sub);
		my $res = $enc_cp932->decode($i_com);
		my @image_md5_array_ref_array = map { [ $image_orig_md5{$_}, $image_conv_md5{$_} ] } keys(%fn);

		# ������{
		my $result = $auto_post_prohibit_instance->prohibit_post_check(
			$new_thread_flag, $age_flag, $thread_no, $newno, $name, $title, $res, $upfile_count,
			\@image_md5_array_ref_array, $idcrypt, \@log, $threadlog_same_user_found_for_suppress_thread_creation
		);

		# ���茋�ʂɂ���āA�X���b�h�쐬�}���A�������́A���_�C���N�g�������s��
		if ($result & AutoPostProhibit::RESULT_THREAD_CREATE_SUPPRESS_REQUIRED) {
			# �X���b�h�쐬�}���Ώ�
			$add_to_threadlog->(); # �V�K���e�L�^�t�@�C���ɒǋL
			error('���̃X���b�h�͍쐬�o���܂���B');
		} elsif ($result & AutoPostProhibit::RESULT_REDIRECT_REQUIRED && $auto_post_prohibit_redirect_url ne '') {
			# ���_�C���N�g�Ώ�
			print "Location: " . URI->new($auto_post_prohibit_redirect_url)->abs($ENV{'REQUEST_URI'}) . "\n\n";
			exit(0);
		}
	}

	# ���e���̖��O�̏����@�\
	if (is_remove_name_target_post($check_i_sub, $i_nam, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, \@remove_name_on_post)) {
		# �Ώۂ̏ꍇ�ɖ��O���폜���A���O���󗓎��̏��������s
		$i_nam = '';
		if ($in_name) { &error("���O�͋L���K�{�ł�"); }
		else { $i_nam = '������'; }
	}

	# reCAPTCHA�F�؎��{����
	my ($is_recaptcha_enabled, $create_log_fh, $create_log_no_delete_fh, $auth_host_log_fh) = 0;
	if ($in{'res'} eq '' && ($recaptcha_thread || exists($in{'g-recaptcha-response'}))) {
		# �X���b�h�쐬��
		# �������O�E�ݐσ��O�EreCAPTCHA�F�ؑΏۃz�X�g���O���I�[�v�����A
		# �폜���O���ݒ茏���ȏォ�AreCAPTCHA�F�ؑΏۃz�X�g�Ɋ܂܂��z�X�g�A
		# �������́AreCAPTCHA���X�|���X�����M����Ă����ꍇ�ɔF�؂��s��
		if (open($create_log_fh, '+>>', $recaptcha_thread_create_log) && flock($create_log_fh, 2) && seek($create_log_fh, 0, 0) # �������O�I�[�v��
			&& open($create_log_no_delete_fh, '+>>', $recaptcha_thread_create_log_no_delete) && flock($create_log_no_delete_fh, 2) && seek($create_log_no_delete_fh, 0, 0) # �ݐσ��O�I�[�v��
			&& open($auth_host_log_fh, '+>>', $recaptcha_thread_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA�F�ؑΏۃz�X�g���O
			# �������O�s���J�E���g�E�����Ώۍs���O
			my $create_log = "����,�X���b�h���쐬�����z�X�g�i�܂��͓o�^ID�j,�^�C���X�^���v\n";
			my $create_count = 0;
			my $is_create_log_changed = 0;
			<$create_log_fh>; # �擪�s�ǂݔ�΂�
			while (<$create_log_fh>) {
				chomp($_);
				my @line = split(/,/, $_);
				if (scalar(@line) == 3) {
					# �����������������A�������Ԃ��o�߂��Ă��Ȃ����O�̂ݎc��
					if ($recaptcha_thread_count_time == 0 || ($line[2] + $recaptcha_thread_count_time >= $time)) {
						$create_log .= "$_\n";
					} else {
						$is_create_log_changed = 1;
					}
					$create_count++; # �J�E���g�͕ʂɍs��
				}
			}
			if ($. < 1 || $is_create_log_changed) {
				seek($create_log_fh, 0, 0);
				truncate($create_log_fh, 0);
				print $create_log_fh $create_log;
			} else {
				seek($create_log_fh, 0, 2);
			}
			$is_recaptcha_enabled = $create_count + 1 > $recaptcha_thread_permit; # �X���b�h�A���쐬�����𒴂��ď������݂����悤�Ƃ��Ă���AreCAPTCHA�F�ؑΏۂ��ǂ���

			# �ݐσ��O �t�@�C���E�擪�s�����݂��Ȃ��ꍇ�͍쐬
			<$create_log_no_delete_fh>; # �擪�s�ǂݔ�΂�
			if ($. < 1) {
				seek($create_log_no_delete_fh, 0, 0);
				truncate($create_log_no_delete_fh, 0);
				print $create_log_no_delete_fh "����,�X���b�h���쐬�����z�X�g�i�܂��͓o�^ID�j,�^�C���X�^���v\n";
			}
			seek($create_log_no_delete_fh, 0, 2);

			# reCAPTCHA�F�ؑΏۃz�X�g���O�m�F
			my $auth_host_log = "����,�X���b�h�^�C�g��,�z�X�g,�^�C���X�^���v\n";
			my $host_found_in_recaptcha_auth_log = 0;
			my $is_auth_host_log_changed = 0;
			<$auth_host_log_fh>; # �擪�s�ǂݔ�΂�
			while (<$auth_host_log_fh>) {
				chomp($_);
				my @line = split(/,/, $_);
				if (scalar(@line) == 4) {
					# ����z�X�g�������������A�F�ؑΏۂƂ���
					if ($line[2] eq $host) {
						$is_recaptcha_enabled = 1;
						$host_found_in_recaptcha_auth_log = 1;
					}
					# �����������������A�������Ԃ��o�߂��Ă��Ȃ����O�̂ݎc��
					if ($recaptcha_thread_auth_host_release_time == 0 || ($line[3] + $recaptcha_thread_auth_host_release_time >= $time)) {
						$auth_host_log .= "$_\n";
					} else {
						$is_auth_host_log_changed = 1;
					}
				}
			}
			# �������O�ł̂�reCAPTCHA�F�ؑΏۂɂȂ����z�X�g�����O�ɒǉ�
			if ($. < 1 || ($is_recaptcha_enabled && !$host_found_in_recaptcha_auth_log)) {
				$auth_host_log .= "$date,$i_sub,$host,$time\n";
				$is_auth_host_log_changed = 1;
			}
			if ($is_auth_host_log_changed) {
				seek($auth_host_log_fh, 0, 0);
				truncate($auth_host_log_fh, 0);
				print $auth_host_log_fh $auth_host_log;
			}
			close($auth_host_log_fh);

			$is_recaptcha_enabled ||= exists($in{'g-recaptcha-response'});
		} else {
			# ���O�t�@�C���I�[�v�����s
			if ($create_log_fh) {
				close($create_log_fh);
			}
			if ($create_log_no_delete_fh) {
				close($create_log_no_delete_fh);
			}
			if ($auth_host_log_fh) {
				close($auth_host_log_fh);
			}
			error("Error: reCAPTCHA");
		}
	} else {
		# ���X��reCAPTCHA�F�؂��L�����AreCAPTCHA���X�|���X�����M����Ă������ɔ�������{����
		$is_recaptcha_enabled = ($in{'res'} ne '' && $recaptcha_res) || exists($in{'g-recaptcha-response'});
	}

	# ���e�L�[�EreCAPTCHA�F��
	if ($is_recaptcha_enabled) {
		# reCAPTCHA�F��
		# reCAPTCHA���\������Ȃ����A�`�F�b�N���s���Ă��Ȃ����Ȃ�
		# reCAPTCHA���X�|���X�����M����Ă��Ă��Ȃ����́AAPI�Ƃ̒ʐM���s��Ȃ�
		my $is_recaptcha_auth_success = 0;
		if ($in{'g-recaptcha-response'} ne '') {
			# reCAPTCHA API�ƒʐM
			my $lwp_ua = LWP::UserAgent->new(timeout => 2);
			my $lwp_response = $lwp_ua->post(
				'https://www.google.com/recaptcha/api/siteverify',
				[ secret => $recaptcha_secret_key, response => $in{'g-recaptcha-response'} ]
			);

			if ($lwp_response->is_success) {
				# ����ɒʐM���s�����ꍇ�ɂ̂ݔF�؏󋵂̊m�F���s��
				my $result = JSON::XS->new()->decode($lwp_response->content);
				if (${$result}{'success'} && Types::Serialiser::is_bool(${$result}{'success'})) {
					# �F�ؐ���
					$is_recaptcha_auth_success = 1;
				}
			} else {
				# �ʐM���s���͔F�ؐ����������̂Ƃ݂Ȃ�
				$is_recaptcha_auth_success = 1;
			}
		}

		# �F�؎��s���̓G���[�\��
		if (!$is_recaptcha_auth_success) {
			if (exists($in{'regikey'}) || !exists($in{'g-recaptcha-response'})) {
				my $back_url;
				# ���e�L�[���n���ꂽ���AreCAPTCHA���X�|���X�t�B�[���h���Ȃ��ꍇ
				if ($in{'res'} eq '') {
					# �V�K�X���b�h�쐬��URL�ɖ߂�
					$back_url = "$readcgi?mode=form";
				} else {
					# �X���b�h��URL�ɖ߂�
					$back_url = "$readcgi?no=$in{'res'}" . ($in{'l'} ? "&l=$in{'l'}" : '');
				}
				error("�O��ʂɖ߂�A�y�[�W���ēǂݍ��݂��ĔF�؂��s���ĉ������B", $back_url);
			} else {
				# reCAPTCHA���\������Ă���y�[�W�������ꍇ�͏]���ʂ�u���E�U�q�X�g���[�Ŗ߂�
				error("�F�؂Ɏ��s���Ă��邩�A�L���������؂�Ă��܂��B");
			}
		}
	} elsif (($in{'res'} eq '' && $regist_key_new) || ($in{'res'} ne '' && $regist_key_res)) {
		# ���e�L�[�`�F�b�N
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			error("���e�L�[�����͕s���ł��B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐�������͂��Ă�������");
		}

		# ���e�L�[�`�F�b�N
		# -1 : �L�[�s��v
		#  0 : �������ԃI�[�o�[
		#  1 : �L�[��v
		local($chk) = &registkey_chk($in{'regikey'}, $in{'str_crypt'});
		if ($chk == 0) {
			error("���e�L�[���������Ԃ𒴉߂��܂����B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐������ē��͂��Ă�������");
		} elsif ($chk == -1) {
			error("���e�L�[���s���ł��B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐�������͂��Ă�������");
		}
	}

	# �A�N�Z�X��IP�A�h���X���擾�ł��Ă���ꍇ�AVPNGate�o�R�̏������݂ł��邩�`�F�b�N
	if ($deny_post_via_vpngate && $addr =~ /^(?:(?:[1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:[1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])$/) {
		# VPNGate �{�����e�B�AVPN�T�[�oIP�A�h���X���݊m�F�p HTTP API�ƒʐM
		my $lwp_ua = LWP::UserAgent->new(timeout => 2);
		my $lwp_response = $lwp_ua->get("http://ipchecker.statistics.api.vpngate.net/api/ipcheck/?key=aepFZyCu&ip=${addr}");

		# ����ɒʐM���s�����ꍇ�ɂ̂�
		# �A�N�Z�X��IP�A�h���X��VPNGate �{�����e�B�AVPN�T�[�o�̂��̂ł��邩�ǂ����̕Ԃ�l���m�F���A
		# VPNGate�o�R�̏������݂������ꍇ�ɃG���[���b�Z�[�W��\��
		if ($lwp_response->is_success && $lwp_response->content >= 1) {
			error("VPNGate����̏������݂͂ł��܂���B");
		}
	}

	# WebProtect �o�^ID�A�g�F��
	if($webprotect_auth) {
		my $auth_result = WebProtectAuth::authenticate($in{'user_id'}, $in{'user_pwd'});
		if($auth_result == WebProtectAuth::ID_NOTFOUND) {
			&error($webprotect_auth_id_notfound_msg);
		} elsif($auth_result == WebProtectAuth::PASS_MISMATCH) {
			&error($webprotect_auth_pass_mismatch_msg);
		} elsif($auth_result != WebProtectAuth::SUCCESS) {
			&error("�F�؃G���[���������܂����B�Ǘ��҂ɂ��A���������B");
		}
	}

	# �g���b�v
	$i_nam2 = &trip($i_nam);

	# �p�X���[�h�Í���
	my $pwd;
	if ($in{'pwd'} ne "") { $pwd = &encrypt($in{'pwd'}); }

	# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ڑ�
	my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);

	# �X���b�h���O�������ݗp����ID
	my $threadlog_write_history_id = do {
		if (defined($chistory_id)) {
			if ($in{save_history}) {
				# �u�������ݗ����ɋL�^����v�`�F�b�N��
				"$chistory_id";
			} else {
				# �u�������ݗ����ɋL�^����v���`�F�b�N��
				"$chistory_id@";
			}
		} else {
			# ����ID�������Ƃ�
			'';
		}
	};

	# �V�K���e�i�V�K�X���b�h�쐬�j
	if ($in{'res'} eq "") {

		# �Ǘ��҃X�����ă`�F�b�N
		if ($createonlyadmin && $pass ne $in{'pwd'}) {
			&error("�X���b�h�̍쐬�͊Ǘ��҂݂̂ɐ�������Ă��܂�");
		}

		# �ϐ��錾
		local($i, $flg, $new_log, @tmp, $top_log, $faq_log);

		# index�W�J
		<$nowfile_fh>; # �擪�s�ǂݔ�΂�
		while(<$nowfile_fh>) {
#			local($sub,$key) = (split(/<>/))[1,6];
			chomp($_);
			local($no,$sub,$re,$nam,$d,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);

			$i++;
			# �X���b�h���d��
			my $checksub = $sub;
			$checksub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
			if ($checksub eq $in{'sub'}) {
				$flg++;
				last;
			} elsif ($key == 2) {
				$top_log .= "$_\n";
				next;
			} elsif ($key == 3) {
				$faq_log .= "$_\n";
				next;
			}

			# �K�萔�I�[�o�[��@tmp���
			if ($i >= $i_max) {
				push(@tmp,"$no<>$sub<>$re<>$nam<>$d<>$na2<>-1<>$upl<>$ressub<>$restime<>$host<>\n");

			# �K�萔����@new���
			} else {
				$new_log .= "$_\n";
			}
		}

		# �X���b�h���d���̓G���[
		if ($flg) {
			close($nowfile_fh);
			close($threadlog_fh);
			&error("<b>�u$in{'sub'}�v</b>�͊����X���b�h�Əd�����Ă��܂��B<br>�ʂ̃X���b�h�����w�肵�Ă�������");
		}

		# ���sindex�X�V
		$new_log = "$new<>$i_sub<>0<>$i_nam2<>$date<>$i_nam2<>1<>$upl_flg<><>$time<>$host<>\n" . $new_log;
		$new_log = $faq_log . $new_log if ($faq_log);
		$new_log = $top_log . $new_log if ($top_log);
		$new_log = "$new<>$host<>$time<>\n" . $new_log;
		seek($nowfile_fh, 0, 0);
		print $nowfile_fh $new_log;
		truncate($nowfile_fh, tell($nowfile_fh));
		close($nowfile_fh);

		# �ߋ����O�ɗ�����X���b�h�̃t���O��ύX
		@tmp2 = @tmp;

		foreach my $tmp2 (@tmp2) {
			local($pastno) = split(/<>/, $tmp2);
			if ($pastno == '') { last; }

			# �X���b�h�ǂݍ���
			my $logfile_path = get_logfolder_path($pastno) . "/$pastno.cgi";
			open(my $pastlog_fh, '+<', $logfile_path) || &error("Open Error: $pastno.cgi");
			flock($pastlog_fh, 2) || error("Lock Error: $pastno.cgi");
			my $file = '';

			# �擪�s�𒊏o�E�������A�t���O�ύX�E�X���b�h�X�V
			my $top = <$pastlog_fh>;
			my ($no,$sub,$res,undef) = split(/<>/, $top);
			$file .= "$no<>$sub<>$res<>-1<>\n";

			# �X���b�h�c��̍s��ǂݍ���
			{
				local $/ = undef;
				$file .= <$pastlog_fh>;
			}

			seek($pastlog_fh, 0, 0);
			print $pastlog_fh $file;
			truncate($pastlog_fh, tell($pastlog_fh));
			close($pastlog_fh);

			# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ŁA�ߋ����O�ɗ������X���b�h�����A�b�v�f�[�g
			$updatelog_db->update_threadinfo($pastno, undef, 0);
		}

		# �ߋ�index�X�V
		if (@tmp > 0) {

			$j = @tmp;
			open(my $pastfile_fh, '+<', $pastfile) || &error("Open Error: $pastfile");
			flock($pastfile_fh, 2) || error("Lock Error: $pastfile_fh");
			while(<$pastfile_fh>) {
				$j++;
				if ($j > $p_max) {
					local($delno) = split(/<>/);

					# ���O�W�J
					my $logfile_path = get_logfolder_path($delno) . "/$delno.cgi";
					open(my $delthread_fh, $logfile_path);
					<$delthread_fh>;
					while (my $line = <$delthread_fh>) {
						$line =~ s/(?:\r\n|\r|\n)$//;

						my ($tim, %upl);
						($tim, $upl{1}, $upl{2}, $upl{3}, $upl{4}, $upl{5}, $upl{6}) = (split/<>/, $line)[11 .. 14, 23 .. 25];

						# �摜�폜
						foreach $i (1 .. 6) {
							my ($img_folder_number, $ex) = split(/,/, $upl{$i});

							if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
								unlink("$upldir/$img_folder_number/$tim-$i$ex");
							}
							# �T���l�C���摜�t�@�C�������݂�����폜
							if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
								unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
							}
						}
					}
					close($delthread_fh);

					unlink($logfile_path);

					# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X����ߋ����O����폜���ꂽ�X���b�h�����폜
					$updatelog_db->delete_threadinfo($delno);

					next;
				}
				push(@tmp,$_);
			}
			seek($pastfile_fh, 0, 0);
			print $pastfile_fh @tmp;
			truncate($pastfile_fh, tell($pastfile_fh));
			close($pastfile_fh);
		}

		# �X���b�h�X�V
		my $logfolder_path = get_logfolder_path($new);
		my $logfile_path = "$logfolder_path/$new.cgi";
		if (!-e $logfolder_path) { # �ۑ��t�H���_���Ȃ��ꍇ�͐V�K�쐬
			mkdir($logfolder_path);
			chmod(0777, $logfolder_path);
		}
		open($log_fh, '+>', $logfile_path) || &error("Write Error: $new.cgi");
		print $log_fh "$new<>$i_sub<>$newno<>1<>\n";
		print $log_fh join('<>',
			'1',
			$in{'sub'},
			$i_nam2,
			$in{'email'},
			$i_com,
			$date,
			$host,
			$pwd,
			$in{'url'},
			$in{'mvw'},
			$my_id,
			$time,
			"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
			"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
			"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
			$idcrypt,
			$in{'user_id'},
			'', # �X���b�h�쐬���Ȃ̂ŁAsage�t���b�O�͏��false
			$cookie_a->value(),
			$threadlog_write_history_id,
			$useragent,
			$is_private_browsing_mode,
			$first_cookie->get_first_access_datetime(),
			"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
			"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
			"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
			"\n"
		);
		close($log_fh);

		# �p�[�~�b�V�����ύX
		chmod(0666, $logfile_path);

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɍ쐬�����X���b�h�����L�^
		$updatelog_db->create_threadinfo($new, $time, 1);

		# ���t�ʃX���b�h�쐬�����O�t�@�C�� �쐬���J�E���g�A�b�v
		&regist_log_countup($thread_create_countlog);

		# �V�K���e�L�^�t�@�C���ɒǋL
		$add_to_threadlog->();

		&sendmail if ($mailing);

	# �ԐM���e
	} else {

		# �A�����e�`�F�b�N
#		local($top);
#		open(IN,"$nowfile") || &error("Open Error: $nowfile");
#		$top = <IN>;
#		close(IN);
#
#		local($no,$hos2,$tim2) = split(/<>/, $top);
#		if ($host eq $hos2 && $wait_response > time - $tim2) {
#			&error("�A�����e�͂������΂炭���Ԃ������ĉ�����");
#		}

		# �擪�t�@�C���𒊏o�E����
		local ($no, $thread_title, $res, $key) = @{$log[0]};

		# �X���b�h�^�C�g���ɂ�铊�e�Ԋu�̕ύX�@�\
		# ���e�Ԋu�E���O�t�@�C���̌���
		my $wait_response = $wait_response_default;
		my $responselog = $responselog_default;
		if (defined($mu->universal_match([$thread_title], [$wait_response_word1], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response1;
			$responselog = $responselog1;
		} elsif (defined($mu->universal_match([$thread_title], [$wait_response_word2], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response2;
			$responselog = $responselog2;
		} elsif (defined($mu->universal_match([$thread_title], [$wait_response_word3], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			$wait_response = $wait_response3;
			$responselog = $responselog3;
		}

		# �A�����eIP/�o�^ID�`�F�b�N�E���X���e���O�ւ̋L�^���e���쐬(�܂��������݂͍s��Ȃ�)
		my $reslog_contents = "$postLimitComparisonFirstItem<>$time<>$user_id_is_post_limit_comparision_item<>\n";
		open(my $reslog_fh, '+<', $responselog) || &error("Open Error: $responselog");
		flock($reslog_fh, 2) || &error("Lock Error: $responselog");
		seek($reslog_fh, 0, 0);
		{
			my $record_count = 1; # ���O����
			while(<$reslog_fh>) {
				chomp($_);
				if ($_ eq '') {
					next;
				}
				my ($record_user_id_or_host, $post_time, $record_first_item_type) = split(/<>/);
				# �������ԓ����ǂ�������
				if ($post_time + $wait_response > $time) {
					# ���ꃆ�[�U�[���ǂ�������
					if ($record_first_item_type == $user_id_is_post_limit_comparision_item && $record_user_id_or_host eq $postLimitComparisonFirstItem) {
						close($reslog_fh);
						&error("�A�����e�͂������΂炭���Ԃ������ĉ�����");
					} elsif ($record_count < $hostnum) {
						# �������ԓ��̑����[�U�[�̃��O���L�^���e�ɒǉ�
						$reslog_contents .= "$_\n";
						$record_count++;
					}
				}
			}
		}

		# ���b�N�`�F�b�N
		if ($key eq '0' || $key eq '2') {
			close($log_fh);
			&error("���̃X���b�h�̓��b�N���̂��ߕԐM�ł��܂���");
		}

		# �ߋ����O�`�F�b�N
		if ($key eq '-1') {
			close($log_fh);
			&error("�ߋ����O�̃X���b�h�ɂ͕ԐM�ł��܂���");
		}

		# �d�����e����
		my ($lastres_com, $lastres_host, $lastres_user_id, $lastres_cookie_a, $lastres_history_id) = @{$log[$#log]}[4, 6, 16, 18, 19];
		$lastres_history_id =~ s/\@$//; # ����ID������@������ꍇ�͎�菜��
		if (is_duplicate_post(
			$thread_title,
			$upl_flg, $i_com, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $host,
			$lastres_com, $lastres_cookie_a, $lastres_user_id, $lastres_history_id, $lastres_host,
			\@duplicate_post_restrict_thread
		)) {
			error("�d�����e�͋֎~�ł�");
		}

		# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑��
		my $is_ngthread_name_override = $newno <= $ngthread_thread_list_creator_name_override_max_res_no && ngthread_name_override_judge($i_nam2, $in{'user_id'}, $cookie_a, $chistory_id, $log[1]);

        # �z�X�g�Ȃǂɂ��age�̖���
        if ($mu->is_disable_age($check_i_sub, $host, $useragent, $cookie_a->value(), $user_id_on_cookie, $chistory_id, $is_private_browsing_mode, \@disable_age)) {
            # �ݒ�ɍ��v����ꍇ�͋����I��sage���e�Ƃ���
            $in{'sage'} = '1';
        }

		# �L�����`�F�b�N
		if ($m_max < $newno) { &error("�ő�L�������I�[�o�[�������ߓ��e�ł��܂���"); }
		elsif ($m_max == $newno) { $maxflag = 1; }
		else { $maxflag = 0; }

		# ID���쐬
		if($idkey) { &makeid; }
		else { $idcrypt = "";}

		# �X���b�h�X�V
#		$res++;
#		unshift(@file,"$no<>$sub<>$res<>$key<>\n");
		$file = "$no<>$i_sub<>$newno<>$key<>\n" . $file;
		$file .= join('<>',
			$newno,
			$in{'sub'},
			$i_nam2,
			$in{'email'},
			$i_com,
			$date,
			$host,
			$pwd,
			$in{'url'},
			$in{'mvw'},
			$my_id,
			$time,
			"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
			"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
			"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
			$idcrypt,
			$in{'user_id'},
			$in{'sage'},
			$cookie_a->value(),
			$threadlog_write_history_id,
			$useragent,
			$is_private_browsing_mode,
			$first_cookie->get_first_access_datetime(),
			"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
			"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
			"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
			"\n"
		);

		seek($log_fh, 0, 0);
		print $log_fh $file;
		truncate($log_fh, tell($log_fh));
		close($log_fh);

		## �K��L�����I�[�o�̂Ƃ� ##
		if ($maxflag) {

			# �ߋ����Oindex�ǂݍ���
			open(my $pastfile_fh, '+<', $pastfile) || &error("Open Error: $pastfile");
			flock($pastfile_fh, 2) || &error("Lock Error: $pastfile");
			my $file;
			{
				local $/ = undef;
				$file = <$pastfile_fh>;
			}

			# ���s���Oindex����Y���X���b�h�����o��
			local($top, $new_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$d,$na2,$key,$upl,undef,undef,$host) = split(/<>/);

				if ($in{'res'} == $no) {
					$re++;
					if ($is_ngthread_name_override) {
						# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑��
						# �X���b�h�쐬�Җ��𓊍e�Җ��ŏ㏑������
						$nam = $i_nam2;
					}
					$file = "$no<>$sub<>$newno<>$nam<>$date<>$na2<>-1<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $file;
					next;
				}
				$new_log .= "$_\n";
			}

			# ���s���Oindex�X�V
			$new_log = $top . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);

			# �ߋ����Oindex�X�V
			seek($pastfile_fh, 0, 0);
			print $pastfile_fh $file;
			truncate($pastfile_fh, tell($pastfile_fh));
			close($pastfile_fh);

		## �\�[�g���� (age) ##
		} elsif ($in{'sage'} ne '1') {

			# index�t�@�C���X�V
			local($flg, $top, $new_log, $top_log, $faq_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$da,$na2,$key,$upl,undef,undef,$host) = split(/<>/);

				if ($key == 2) {
					$top_log .= "$_\n";
					next;
				}
				if ($key == 3 && $in{'res'} != $no) {
					$faq_log .= "$_\n";
					next;
				}
				if ($key == 3 && $in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑��
						# �X���b�h�쐬�Җ��𓊍e�Җ��ŏ㏑������
						$nam = $i_nam2;
					}
					$faq_log = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $faq_log;
					next;
				} elsif ($in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑��
						# �X���b�h�쐬�Җ��𓊍e�Җ��ŏ㏑������
						$nam = $i_nam2;
					}
					$new_log = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>\n" . $new_log;
					next;
				}
				$new_log .= "$_\n";
			}

			if (!$flg) {
				&error("�Y���̃X���b�h��index�t�@�C���Ɍ�������܂���");
			}

			local($no2,$host2,$time2) = split(/<>/, $top);

#			unshift(@new,$new);
			$new_log = $faq_log . $new_log if ($faq_log);
			$new_log = $top_log . $new_log if ($top_log);
			$new_log = "$no2<>$host<>$time<>\n" . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);

		## �\�[�g�Ȃ� (sage) ##
		} else {

			# index�t�@�C���X�V
			local($flg, $top, $new_log);
			$top = <$nowfile_fh>;
			while(<$nowfile_fh>) {
				chomp($_);
				local($no,$sub,$re,$nam,$da,$na2,$key,$upl,undef,undef,$host) = split(/<>/);
				if ($in{'res'} == $no) {
					$flg = 1;
					if ($is_ngthread_name_override) {
						# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑��
						# �X���b�h�쐬�Җ��𓊍e�Җ��ŏ㏑������
						$nam = $i_nam2;
					}
					$_ = "$in{'res'}<>$sub<>$newno<>$nam<>$date<>$i_nam2<>$key<>$upl<>$in{'sub'}<>$time<>$host<>";
				}
				$new_log .= "$_\n";
			}

			if (!$flg) {
				&error("�Y���̃X���b�h��index�t�@�C���Ɍ�������܂���");
			}

			local($no2,$host2,$time2) = split(/<>/, $top);

			$new_log = "$no2<>$host<>$time<>\n" . $new_log;
			seek($nowfile_fh, 0, 0);
			print $nowfile_fh $new_log;
			truncate($nowfile_fh, tell($nowfile_fh));
			close($nowfile_fh);
		}

		# FAQ�J�E���g
#		&faqcount ($i_com,$in{'res'});

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ŁA�X���b�h�����A�b�v�f�[�g
		$updatelog_db->update_threadinfo($in{'res'}, $time, !$maxflag ? 1 : 0);

		# ���t�ʃ��X�������ݐ����O�t�@�C�� �������ݐ��J�E���g�A�b�v
		&regist_log_countup($response_countlog);

		# ���X���e���O�֋L�^
		seek($reslog_fh, 0, 0);
		print $reslog_fh $reslog_contents;
		truncate($reslog_fh, tell($reslog_fh));
		close($reslog_fh);

		# ���[�����M
		&sendmail if ($mailing == 2);

		# ���X���m�点���[�����M
		&sendnotify if ($mailnotify != 0);
	}

	# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ؒf
	$updatelog_db->close(0);

	# �o�^ID�F�ؐ������O�֋L�^
	if($webprotect_auth && $webprotect_authlog) {
		local $/ = undef;
		my $tmp = "$in{'user_id'}<>$date\n";
		open(my $webprotect_authlog_fh, '+<', $webprotect_authlog_path) || &error("Open Error: $webprotect_authlog_path");
		flock($webprotect_authlog_fh, 2) || &error("Open Error: $webprotect_authlog_path");
		$tmp .= <$webprotect_authlog_fh>;
		seek($webprotect_authlog_fh, 0, 0);
		print $webprotect_authlog_fh $tmp;
		truncate($webprotect_authlog_fh, tell($webprotect_authlog_fh));
		close($webprotect_authlog_fh);
	}

	# reCAPTCHA�F�� �������O/�ݐσ��O�ǋL
	if ($in{'res'} eq '' && ($recaptcha_thread || $is_recaptcha_enabled)) {
		my $host_or_user_id = $webprotect_auth ? $in{'user_id'} : $host;
		my $recaptcha_thread_create_log_append_contents = "$date,$host_or_user_id,$time\n";
		if ($create_log_fh) {
			if ($recaptcha_thread_create_log_append_contents ne '') {
				print $create_log_fh $recaptcha_thread_create_log_append_contents;
			}
			close($create_log_fh);
		}
		if ($create_log_no_delete_fh) {
			if ($recaptcha_thread_create_log_append_contents ne '') {
				print $create_log_no_delete_fh $recaptcha_thread_create_log_append_contents;
			}
			close($create_log_no_delete_fh);
		}
	}

	# �������݃��O�o�͋@�\
	if ($post_log) {
		my $post_log_filepath = do {
			my $log_dir = File::Spec->canonpath($post_log_dir); # �o�̓f�B���N�g���p�X���K��
			my $date = strftime('%Y%m%d', @localtime); # ���t�t�H�[�}�b�g
			File::Spec->catfile($log_dir, $date . $post_log_filename_suffix); # �o�̓t�@�C���p�X���쐬
		};
		my $post_log_fh;
		if (open($post_log_fh, '>>', $post_log_filepath) && flock($post_log_fh, 2)) { # �t�@�C���𐳏�ɃI�[�v���E���b�N�ł����ꍇ�̂ݏ����݂���
			# �t�@�C������̏ꍇ�ɂ́A�w�b�_�[�s��ǉ�
			if (-s $post_log_filepath == 0) {
				# �w�b�_�[��`
				my @header = (
					'����',
					'$bbs_pass',
					'�X���b�h�ԍ�',
					'�X���b�h��',
					'�J�e�S��',
					'�X���쐬or���X',
					'���X�ԍ�',
					'���O',
					'age�Asage',
					'���[�U�[ID',
					'�v���C�x�[�g���[�h',
					'����A�N�Z�X����',
					'CookieA���s',
					'���j�[�NCookieA',
					'�o�^ID',
					'����ID',
					'�z�X�g',
					'������',
					'���X���e'
				);
				foreach my $i (1 .. 6) {
					push(@header,
						"�摜$i",
						"�摜${i}��MD5�i�ϊ��O�j",
						"�摜${i}��MD5�i�ϊ���j"
					);
				}
				push(@header, 'UserAgent');

				# �w�b�_�[�o��
				print $post_log_fh join(',', @header) . "\n";
			}

			# �������ݍ��ڃZ�b�g
			my $thread_no = $in{'res'} eq '' ? $new : $in{'res'};         # �X���b�h�ԍ�
			(my $sub = $i_sub) =~ tr/,//d;                                # �J���}���������X���b�h��
			my $category = do {                                           # �J�e�S��
				my $tmp_category = '-';
				my $tmp_sub = $enc_cp932->decode($sub); # �X���b�h������v����̂��ߓ���������֕ϊ�
				foreach my $conv_set (@category_convert) {
					my $decoded_conv_set = $enc_cp932->decode($conv_set); # �ϊ��Z�b�g����v����̂��ߓ���������֕ϊ�
					my ($keyword, $cat) = split(/:/, $decoded_conv_set, 2);
					if ($keyword eq '') {
						next; # �J�e�S���L�[���[�h����̎��̓X�L�b�v
					}
					my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
					if ($tmp_sub =~ /$capture_regex/) {
						# �Ή�����J�e�S������ݒ�
						$tmp_category = $enc_cp932->encode($cat);
						# �X���b�h������J�e�S���L�[���[�h�������čăZ�b�g
						$tmp_sub = $1;
						$sub = $enc_cp932->encode($tmp_sub);
						last;
					}
				}
				$tmp_category;
			};
			my $formatted_date = do { # ���t
				my ($sec, $min, $hour, $mday, $mon, $year) = @localtime[0..5];
				sprintf("%s/%02d/%02d %02d:%02d:%02d", substr($year+1900, -2), $mon+1, $mday, $hour, $min, $sec);
			};
			my $post_type = $in{'res'} eq '' ? '�X���쐬' : '���X';       # �X���쐬 or ���X
			my $res_no = $in{'res'} eq '' ? 1 : $newno;                   # ���X�ԍ�
			(my $nam = $i_nam2) =~ tr/,//d;                               # �J���}�����������O
			my $sage = $in{'res'} ne '' ? ($in{'sage'} eq '1' ? 'sage' : 'age') : '-'; # age / sage
			my $idcrypt = $idcrypt ne '' ? $idcrypt : '-';                # ���[�U�[ID
			my $private_browsing_mode = $is_private_browsing_mode ? '�L��' : '-'; # �v���C�x�[�g�u���E�W���O���[�h
			my $first_access_time = $first_cookie->value(1) || '-'; # ����A�N�Z�X����
			my $issuing_cookie_a = $is_cookie_a_issuing ? '���s' : '-';   # CookieA�𔭍s�������ǂ���
			my $post_log_cookie_a = $cookie_a->value() ne '' ? $cookie_a->value() : '-'; # ���j�[�NCookieA
			my $user_id = exists($in{'user_id'}) ? $in{'user_id'} : '-';  # �o�^ID
			my $history_id = $chistory_id ne '' ? $chistory_id : '-';      # ����ID
			# ���X���e�̕��������擾
			my $res_length = do {
				my $normalized_res = $enc_cp932->decode($i_com);
				$normalized_res =~ s/<br>//g;
				$normalized_res = HTML::Entities::decode($normalized_res);
				length($normalized_res);
			};
			(my $com = $i_com) =~ tr/,//d;                                # �J���}�����������X���e���擾
			$com = replace_contents_for_post_log($com);                   # ���X���e���u�������݃��O�̒u���L�^�@�\�v�̐ݒ�l�ɉ����Ēu��
			if ($com eq '') { $com = '-'; }                               # ���X���e����̏ꍇ�Ɂu-�v���Z�b�g
			my @imgs; # �摜1�`6, �摜1�`6��MD5(�ϊ��O), �摜1�`6��MD5(�ϊ���)���i�[����z��
			foreach my $i (1 .. 6) {
				my $img = $ex{$i} ne '' ? "$fn{$i}/$time-$i$ex{$i}" : '-'; # �摜1�`6
				my $img_orig_md5 = $image_orig_md5{$i} ne '' ? $image_orig_md5{$i} : '-'; # �摜1�`6��MD5�i�ϊ��O)
				my $img_conv_md5 = $image_conv_md5{$i} ne '' ? $image_conv_md5{$i} : '-'; # �摜1�`6��MD5�i�ϊ���)
				push(@imgs, $img, $img_orig_md5, $img_conv_md5);
			}
			my $useragent = $useragent ne '' ? $useragent : '-';          # UserAgent

			# �������݃��O�ɒǋL
			print $post_log_fh join(',',
				$formatted_date, # ����
				$bbs_pass, # $bbs_pass
				$thread_no, # �X���b�h�ԍ�
				$sub, # �X���b�h��
				$category, # �J�e�S��
				$post_type, # �X���쐬or���X
				$res_no, # ���X�ԍ�
				$nam, # ���O
				$sage, # age�Asage
				$idcrypt, # ���[�U�[ID
				$private_browsing_mode, # �v���C�x�[�g���[�h
				$first_access_time, # ����A�N�Z�X����
				$issuing_cookie_a, # CookieA���s
				$post_log_cookie_a, # ���j�[�NCookieA
				$user_id, # �o�^ID
				$history_id, # ����ID
				$host, # �z�X�g
				$res_length, # ������
				$com, # ���X���e
				@imgs, # �摜1�`6, �摜1�`6��MD5(�ϊ��O), �摜1�`6��MD5(�ϊ���)
				$useragent # UserAgent
			) . "\n";
		}
		close($post_log_fh);
	}

	# �N�b�L�[���i�[
	if ($in{'cook'} eq 'on') {
		# Cookie�擾
		my @cookie = get_cookie();

		# �u�X���b�h���g�b�v�փ\�[�g�v/�usage�v Cookie�擾
		my ($cthread_sort, $thread_sage) = @cookie[7,8];

		# �ԐM���e���̂݁A�t�H�[������́usage�v�`�F�b�N��Ԃŏ㏑��
		if($in{'res'} ne '') {
			$thread_sage = $in{'sage'} eq '1' ? '1' : '0';
		}

		# WebProtect �o�^ID
		my ($user_id, $user_pwd) = do {
			if (($in{'res'} eq '' && $webprotect_auth_new) || ($in{'res'} ne '' && $webprotect_auth_res)) {
				# �o�^ID�F�؂��L���̏ꍇ�A�t�H�[�����͒l���g�p
				($in{'user_id'}, $in{'user_pwd'});
			} else {
				# �o�^ID�F�؂������̏ꍇ�A����Cookie�ɃZ�b�g����Ă���l���g�p
				@cookie[5,6];
			}
		};

		# �������ݗ����ɋL�^���� �t���O
		my $save_history = $cookie[9];
		if (exists($in{save_history})) {
			# �t�H�[������`�F�b�N�{�b�N�X�̏�Ԃ����M����Ă����ꍇ�̂݁A
			# Cookie�ɏ㏑���L�^����
			$save_history = int($in{save_history}) ? 1 : 0;
		}

		# ���O��
		my $name = $is_hide_name_field_in_form ? $cookie[0] : $i_nam; # ���O����\���@�\�K�p���́ACookie�̒l�������p��

		# 3���ȏ�A�b�v���[�h���� �`�F�b�N�t���O
		my $increase_upload_num_checked = $cookie[10];
		if (exists($in{'increase_num'})) {
			$increase_upload_num_checked = $in{'increase_num'} eq '1';
		}

		# Cookie �Z�b�g
		&set_cookie($name, $in{email}, $in{pwd}, $in{url}, $in{mvw}, $user_id, $user_pwd, $cthread_sort, $thread_sage, $save_history,
			$increase_upload_num_checked);
	}

	# �������ݗ������O�ɋL�^
	my $decoded_check_i_sub = $enc_cp932->decode($check_i_sub);
	if ($in{save_history} && defined($chistory_id) && $chistory_id ne ''
		&& scalar(grep { $_ ne '' && index($decoded_check_i_sub, $_) != -1 } @history_save_exempt_titles) == 0) {
		# �������݃X���b�h��������
		my $thread_no = int($in{'res'} eq '' ? $new : $in{'res'}); # �X���b�h�ԍ�
		my $res_no = int($in{'res'} eq '' ? 1 : $newno);           # ���e���XNo.
		# �������ݗ������O�ɋL�^
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->add_post_history($thread_no, $res_no, int($time));
		$history_log->DESTROY();
	}

	# �������b�Z�[�W
	&header;
	$md = 'view';
	if ($in{'res'} eq "") { $no = $new; }
	else { $no = $in{'res'}; }

	print <<EOM;
<br><br><div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="400">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center" height="60">
	<h3 style="font-size:15px">�����e���肪�Ƃ��������܂���</h3>
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
EOM

	# �ߋ����O�J��z���̏ꍇ
	if ($maxflag) {
		print "�������P�X���b�h����̍ő�L�����𒴂������߁A<br>\n";
		print "���̃X���b�h�� <a href=\"$readcgi?mode=past\">�ߋ����O</a> ";
		print "�ֈړ����܂����B\n";
		$md = 'past';
	}

	# �߂�t�H�[��
	print <<"EOM";
<table><tr><td valign="top">
<form action="$bbscgi">
<input type="submit" value="�f���֖߂�">
</form></td><td width="15"></td>
<td valign="top">
<form action="$readcgi" method="post">
<input type="hidden" name="mode" value="$md">
<input type="hidden" name="no" value="$no">
<input type="submit" value="�X���b�h������">
</form></td>
</tr>
</table>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �L���폜�i�g���ĂȂ��悤�Ȃ̂ō폜�j
#-------------------------------------------------
# sub delete {}


#-------------------------------------------------
#  �����e����
#-------------------------------------------------
sub mente {
	# �����`�F�b�N
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# �L���C��
	if ($in{'job'} eq "edit") {
		if ($in{'pwd'} eq '') { &error("�p�X���[�h�̓��̓����ł�"); }

		require $editlog;
		&edit_log("user");

	# �폜����
	} elsif ($in{'job'} eq "del") {

		if ($in{'pwd'} eq '') { &error("�p�X���[�h�̓��̓����ł�"); }

		# �X���b�h���폜�L�����o
		my ($flg, $top, $check, $new_log, $last_tim, $last_nam, $last_dat, $last_sub);
		my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		my $res = (split(/<>/, $top))[2]; # ���O�ɋL�^���郌�X�����擾
#		$j=-1;
		my $res_cnt = 0; # �ŏI���X��񌈒�p���X���J�E���^ (���O�ɋL�^���郌�X����$res�����̂܂܎g�p)
		while(<DAT>) {
			local($no,$sub,$nam,$eml,$com,$dat,$ho,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl{4},$upl{5},$upl{6}) = split(/<>/);

			# �X���b�h���ň�ԍŌ�ɍX�V���ꂽ�L���̎������o����
#			if ($tim ne 0 && $tim > $lrtime) { $lrtime = $tim; }

			if ($in{'no'} == $no) {
				$flg = 1;

				# �Ǘ��p�X���[�h�ō폜
				if ($in{'pwd'} ne $pass) {
					# �p�X�ƍ�
					$check = &decrypt($in{'pwd'}, $pw);
				}

				# �X���b�h�w�b�_�̃��X���𒲐�
#				($num,$sub2,$res,$key) = split(/<>/, $top);
#				$res--;
#				$top = "$num<>$sub2<>$res<>$key<>\n";

				# �Y�t�폜
				foreach my $i (1 .. 6) {
					my ($img_folder_number, $ex) = split(/,/, $upl{$i});

					if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
						unlink("$upldir/$img_folder_number/$tim-$i$ex");
					}
					# �T���l�C���摜�t�@�C�������݂�����폜
					if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
						unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
					}
				}

				# �폜�����Ȃ�X�L�b�v
#				$j++;
				next;
			}
			$new_log .= $_;
			$res_cnt++;

			# �X���b�h���ň�ԍŌ�ɍX�V���ꂽ�L���̎������o����
			if ($tim ne 0 && $tim > $last_tim) { $last_tim = $tim; }

			# �ŏI�L���̓��e�҂Ǝ��Ԃ��o���Ă���
			$last_nam = $nam;
			$last_dat = $dat;
			# �^�C�g����
			$last_sub = $sub;
		}

		if (!$flg) { &error("�Y���L������������܂���"); }
#		if (!$check) { &error("�p�X���[�h���Ⴂ�܂�"); }
		if (!$check && $in{'pwd'} ne $pass ) { &error("�p�X���[�h���Ⴂ�܂�"); }

		$res_cnt--; # ���X�J�E���g����e���X������
		if ($res_cnt == 0) {
			# �ŏI�I�Ƀ��X���Ȃ��ꍇ
#			$last_nam = "";
#			$last_dat = "";
			$last_sub = "";
#			$last_tim = "";
		}

		# �X���b�h�X�V
		$new_log = $top . $new_log;
		seek(DAT, 0, 0);
		print DAT $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# index�W�J
		my ($top_log, $faq_log, @new, @sort) = ('', '');
#		local($top, @sort, @top, @faq);
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			chomp($_);
			local($no,$sub,$re,$nam,$dat,$na2,$key,$upl) = split(/<>/);

			if ($key == 2) {
				$top_log .= "$_\n";
				next;
			}
			if ($key == 3 && $in{'f'} != $no) {
				$faq_log .= "$_\n";
				next;
			}
			if ($key == 3 && $in{'f'} == $no) {
				# index�̃��X���𒲐����A�ŏI���e�҂Ǝ��Ԃ�u��
#				$res--;
#				$na2 = $last_nam;
#				$dat = $last_dat;
# ���X���Ȃ��ꍇ�́A���X�̃^�C�g�����󗓂�
#				if ($j < 1) {$last_sub="";}
				$faq_log .= "$no<>$sub<>$res<>$nam<>$dat<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>\n";
				next;
			}
			if ($in{'f'} == $no) {
				# index�̃��X���𒲐����A�ŏI���e�҂Ǝ��Ԃ�u��
#				$res--;
#				$na2 = $last_nam;
#				$dat = $last_dat;
# ���X���Ȃ��ꍇ�́A���X�̃^�C�g�����󗓂�
#				if ($j < 1) {$last_sub="";}
				$_ = "$no<>$sub<>$res<>$nam<>$dat<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>";
			}
			push(@new,"$_\n");

			# �\�[�g�p�z��
			$dat =~ s/\D//g;
			push(@sort,$dat);
		}

		# ���e���Ƀ\�[�g
		@new = @new[sort {$sort[$b] <=> $sort[$a]} 0..$#sort];

		# index�X�V
		unshift(@new,$faq_log) if ($faq_log);
		unshift(@new,$top_log) if ($top_log);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ŁA���X�폜��̃X���b�h���ɃA�b�v�f�[�g
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($in{'f'}, $last_tim, undef);
		$updatelog_db->close(0);

		# �������b�Z�[�W
		&header;
		print "<div align=\"center\">\n";
		print "<b>�L���͐���ɍ폜����܂����B</b>\n";
		print "<form action=\"$bbscgi\">\n";
		print "<input type=\"submit\" value=\"�f���֖߂�\"></form>\n";
		print "</div></body></html>\n";
		exit;

	# ���b�N����
	} elsif ($in{'job'} eq "lock") {

		if ($in{'pwd'} eq '') { &error("�p�X���[�h�̓��̓����ł�"); }

		my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";

		# �X���b�h�ꕔ�ǂݍ���
		my $top = <DAT>;
		my $parent_res = <DAT>;

		# �p�X���[�h�`�F�b�N
		local($no,$sb,$na,$em,$com,$da,$ho,$pw) = split(/<>/, $parent_res);

# �Ǘ��҃��b�N
		if ($in{'pwd'} eq $pass) {}
		elsif (!&decrypt($in{'pwd'}, $pw)) { &error("�p�X���[�h���Ⴂ�܂�"); }

		# �X���b�h�c��ǂݍ���
		my $file;
		{
			local $/ = undef;
			$file = <DAT>;
		}

		# �X�V
		local($num,$sub,$res,$key) = split(/<>/, $top);
		if ($in{'pwd'} eq $pass && $key == 4) { $key = 1;}
		elsif ($in{'pwd'} eq $pass ) { $key = 4; }
		elsif ($in{'pwd'} ne $pass && $key == 4) { &error("�Ǘ��҃��b�N����Ă��܂�"); }
		elsif ($key == 1) { $key = 0; }
		elsif ($key == 0) { $key = 1; }
		$top = "$num<>$sub<>$res<>$key<>\n";

		seek(DAT, 0, 0);
		print DAT $top . $parent_res . $file;
		truncate(DAT, tell(DAT));
		close(DAT);

		# index�W�J
		my $new_log;
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			chomp($_);
			local($no,$sub,$res,$nam,$da,$na2,$key2,$upl,$ressub,$restime) = split(/<>/);

			if ($in{'f'} == $no) {
				$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>";
			}
			$new_log .= "$_\n";
		}

		# index�X�V
		$new_log = $top . $new_log;
		seek(DAT, 0, 0);
		print DAT $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �������b�Z�[�W
		&header;
		print "<div align=\"center\">\n";

		if ($key == 4) {
			print "<b>�X���b�h�͊Ǘ��҂ɂ�胍�b�N����܂����B</b>\n";
		} elsif ($key == 1) {
			print "<b>�X���b�h�̓��b�N��������܂����B</b>\n";
		} else {
			print "<b>�X���b�h�̓��b�N����܂����B</b>\n";
		}

		print "<form action=\"$bbscgi\">\n";
		print "<input type=\"submit\" value=\"�f���֖߂�\"></form>\n";
		print "</div></body></html>\n";
		exit;
	}

	# �Y�����O�`�F�b�N
	$flg = 0;
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(IN, $logfile_path);
	$top = <IN>;
	while (<IN>) {
		($no,$sub,$name,$email,$com,$date,$host,$pw) = split(/<>/);

		if ($in{'no'} == $no) {
			$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
			last;
		}
	}
	close(IN);

	# �Ǘ��҂ɂ��ύX���ł���悤�ɖ�����
#	if ($pw eq "") {
#		&error("�Y���L���̓p�X���[�h���ݒ肳��Ă��܂���");
#	}

	($num,$sub2,$res,$key) = split(/<>/, $top);

	&header;
	print <<"EOM";
<div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/mente.gif" align="top">
&nbsp; <b>�����e�t�H�[��</b></td>
<td align="right" bgcolor="$col3" nowrap>
<a href="javascript:history.back()">�O��ʂɖ߂�</a></td>
</tr></table></Td></Tr></Table>
<P>
<form action="$registcgi" method="post">
<input type="hidden" name="mode" value="mente">
<input type="hidden" name="f" value="$in{'f'}">
<input type="hidden" name="no" value="$in{'no'}">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�ΏۃX���b�h</td>
  <td>�����F <b>$sub</b><br>���O�F <b>$name</b>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�����I��</td>
  <td><select name="job">
	<option value="edit" selected>�L�����C��
EOM

	if ($in{'no'} eq "") {
		if ($key == 1) {
			print "<option value=\"lock\">�X���b�h�����b�N\n";
		} elsif ($key == 0) {
			print "<option value=\"lock\">���b�N������\n";
		}
	} else {
		print "<option value=\"del\">�L�����폜\n";
	}

	print <<"EOM";
	</select>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�p�X���[�h</td>
  <td><input type="password" name="pwd" size="10" maxlength="8">
	<input type="submit" value="���M����">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM

	print <<"EOM";
<P>
<form action="$admincgi" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="logfile" value="1">
<input type="hidden" name="no" value="$in{'f'}">
EOM

	if ($in{'no'} eq "") {
	print <<"EOM";
<input type="hidden" name="no2" value="0">
EOM
	} else {
	print <<"EOM";
<input type="hidden" name="no2" value="$in{'no'}">
EOM
	}

	print <<"EOM";
<input type="hidden" name="action" value="view">
<input type="hidden" name="job" value="split">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�Ǘ��҃��[�h</td>
  <td>���̃��X�ŃX���b�h����
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�Ǘ��p�X���[�h</td>
  <td><input type="password" name="pass" size="10" maxlength="8">
	<input type="submit" value="�X���b�h�����i�Ǘ��҂̂݁j">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM

	if ($in{'no'} eq "") {
	print <<"EOM";
<P>
<form action="$admincgi" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="logfile" value="1">
<input type="hidden" name="action" value="del">
<input type="hidden" name="no" value="$in{'f'}">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�Ǘ��҃��[�h</td>
  <td>�X���b�h�폜
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="75" nowrap>�Ǘ��p�X���[�h</td>
  <td><input type="password" name="pass" size="10" maxlength="8">
	<input type="submit" value="�X���b�h�폜�i�Ǘ��҂̂݁j">
  </td></form>
</tr>
</table>
</Td></Tr></Table>
EOM
	}

	print <<"EOM";
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �N�b�L�[���s
#-------------------------------------------------
sub set_cookie {
	local(@cook) = @_;
	local($gmt, $cook, @t, @m, @w);

	@t = gmtime(time + 60*24*60*60);
	@m = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
	@w = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');

	# ���ەW�������`
	$gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
			$w[$t[6]], $t[3], $m[$t[4]], $t[5]+1900, $t[2], $t[1], $t[0]);

	# �ۑ��f�[�^��URL�G���R�[�h
	foreach (@cook) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	# �i�[
	my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}";
	print "Set-Cookie: $cookie_name=$cook; expires=$gmt\n";
}

#-------------------------------------------------
#  ���[�����M
#-------------------------------------------------
sub sendmail {
	local($msub, $mbody, $mcom, $email);

	# ���[���^�C�g�����`
	$msub = "$title�F $i_sub";

	# �{���̉��s�E�^�O�𕜌�
	$mcom = $i_com;
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/��/g;
	$mcom =~ s/&gt;/��/g;
	$mcom =~ s/&quot;/�h/g;
	$mcom =~ s/&amp;/��/g;

$mbody = <<EOM;
--------------------------------------------------------
$title�Ɉȉ��̓��e������܂����̂ł��m�点���܂��B
����̓V�X�e������̎������M���[���ł��B
���f���e�̏ꍇ�͐\\���󂠂�܂��񂪖������Ă��������B
�����ɍ폜���܂��B

���e�����F$date
�z�X�g���F$host
�u���E�U�F$ENV{'HTTP_USER_AGENT'}

���Ȃ܂��F$i_nam2
�d���[���F$in{'email'}
�^�C�g���F$i_sub
�t�q�k  �F$in{'url'}

$mcom

�X���b�h������
$fullscript?&no=$no
--------------------------------------------------------
EOM

	# �薼��BASE64��
	$msub = &base64($msub);

	# ���[���A�h���X���Ȃ��ꍇ�͊Ǘ��҃A�h���X�ɒu������
	if ($in{'email'} eq "") { $email = $mailto; }
	else { $email = $in{'email'}; }

	# sendmail���M
	open(MAIL,"| $sendmail -t -i") || &error("���M���s");
	print MAIL "To: $mailto\n";
	print MAIL "From: $email\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $ver\n\n";
	foreach ( split(/\n/, $mbody) ) {
		&jcode'convert(*_, 'jis', 'sjis');
		print MAIL $_, "\n";
	}
	close(MAIL);
}

#-------------------------------------------------
#  ���X���m�点���M
#-------------------------------------------------
sub sendnotify {
	local($msub,$mbody,$mcom,$email,$no,$sub,@maillist,$eml,$top,$top2,$flg,@maillist2);

	# �X���b�h���
	# �X���b�h�ǂݍ���
	my $logfile_path = get_logfolder_path($in{'res'}) . "/$in{'res'}.cgi";
	open(IN, $logfile_path) || &error("Open Error: $in{'res'}.cgi");
	@file = <IN>;
	close(IN);

	# �擪�t�@�C���𒊏o�A����
	$top = shift(@file);
	($no,$sub,undef,undef) = split(/<>/, $top);
	$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

	# ���[���A�h���X�𒊏o
	# �g�b�v�L��
	$top2 = shift(@file);
	(undef,undef,undef,$eml,undef,undef,undef,undef,undef,undef,undef,undef,undef) = split(/<>/, $top2);
	if ($eml ne "") {
		foreach ( split(/,/, $refuseaddr) ) {
			if (index("$eml",$_) >= 0) {
				$flg = 1; last;
			}
		}
		if ($flg == 0){
			push(@maillist,$eml);
		}
	}

	# ���X�L��
	if ($mailnotify==2 && $#file >= 0) {

		foreach ( @file ){
		# print $value, "\n";
			(undef,undef,undef,$eml,undef,undef,undef,undef,undef,undef,undef,undef,undef) = split(/<>/);
			if ($eml ne "") {
				$flg = 0;
				foreach ( split(/,/, $refuseaddr) ) {
					if (index("$eml",$_) >= 0) {
						$flg = 1; last;
					}
				}
				if ($flg == 0){
					push(@maillist,$eml);
				}
			}
		}
	}

	# ���[���A�h���X�̏d���̍폜
	my %uniq = map {$_ => 1} @maillist;
	my @maillist2 = keys %uniq;

#	my %count;
#	@maillist = grep {!$count{$_}++} @maillist;

#	print "@maillist";

	# ���[���^�C�g�����`
	$msub = "$title�F [$no] $sub";

	# �{���̉��s�E�^�O�𕜌�
	$mcom = $i_com;
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/��/g;
	$mcom =~ s/&gt;/��/g;
	$mcom =~ s/&quot;/�h/g;
	$mcom =~ s/&amp;/��/g;

$mbody = <<EOM;
--------------------------------------------------------
$title��
�u[$no] $sub�v�ɐV�������X������܂����̂ł��m�点���܂��B

�^�C�g���F$i_sub ( No.$newno )
�����F$date
�Ȃ܂��F$i_nam2

$mcom

�X���b�h������
$fullscript?&no=$no
--------------------------------------------------------
EOM

# �g�������ȕϐ�
# $sub
# $new
# $newno
# $fullscript �V��
#	�{���͂����Čf�ڂ��Ȃ��Ƃ����e���A���B
#	�z�X�g���F$host
#	�u���E�U�F$ENV{'HTTP_USER_AGENT'}
#	�d���[���F$in{'email'}
#	�t�q�k  �F$in{'url'}
#	$mcom

	# �薼��BASE64��
	$msub = &base64($msub);

#	$notifybcc = "@maillist2";

	# 1�ʂ����M����
#	while (@maillist) {

	# sendmail���M
	open(MAIL,"| $sendmail -t -i") || &error("���M���s");
	print MAIL "To: $notifyaddr\n";
	print MAIL "Bcc: ";

	# ���[���A�h���X��W�J
	$" = ',';
	print MAIL "@maillist2";
	print MAIL "\n";
	print MAIL "From: $notifyaddr\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $ver\n\n";
	foreach ( split(/\n/, $mbody) ) {
		&jcode'convert(*_, 'jis', 'sjis');
		print MAIL $_, "\n";
	}
	close(MAIL);

#	}
}

#-------------------------------------------------
#  BASE64�ϊ�
#-------------------------------------------------
#	�Ƃقق�WWW����Ō��J����Ă��郋�[�`����
#	�Q�l�ɂ��܂����B( http://tohoho.wakusei.ne.jp/ )
sub base64 {
	local($sub) = @_;
	&jcode'convert(*sub, 'jis', 'sjis');

	$sub =~ s/\x1b\x28\x42/\x1b\x28\x4a/g;
	$sub = "=?iso-2022-jp?B?" . &b64enc($sub) . "?=";
	$sub;
}
sub b64enc {
	local($ch)="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	local($x, $y, $z, $i);
	$x = unpack("B*", $_[0]);
	for ($i=0; $y=substr($x,$i,6); $i+=6) {
		$z .= substr($ch, ord(pack("B*", "00" . $y)), 1);
		if (length($y) == 2) {
			$z .= "==";
		} elsif (length($y) == 4) {
			$z .= "=";
		}
	}
	$z;
}

#-------------------------------------------------
#  �֎~���[�h�`�F�b�N
#-------------------------------------------------
sub no_wd {
	my ($flg, $badword);

	# �����������������p�̕ϐ��ɓ���A�S�ď������ɕϊ�
	my $lc_searchwords = lc("$i_nam $i_sub $i_com $in{'url'}");

	foreach ( split(/,/, $no_wd) ) {
		chomp($_);

		# �������s
		if (index($lc_searchwords, lc($_)) >= 0) {
			# �������ꂽ��������L�^
			if ($badwordlog) {
				open(my $out_fh, '>>', $badwordlog) || &error("Write Error: $badwordlog");
				flock($out_fh, 2);
				print $out_fh "$_\t$i_nam\t$i_sub\t$i_com\t$in{'url'}\t$date\t$time\t$host\n";
				close($out_fh);
			}
			$badword = $_;
			$flg = 1;
			last;
		}
	}

	if ($flg) { &error("�֎~���[�h $badword ���܂܂�Ă��܂�"); }
}

#-------------------------------------------------
#  ���O����NG���[�h����(�֎~������E���͋������`�F�b�N)
#-------------------------------------------------
sub ng_nm {
	if($ng_nm || @permit_name_regex) {
		my $ng_flg = 0;

		# NG���[�h��������g���b�v�L�[�����O���A����������ɕϊ�
		my $utf8flagged_name = $enc_cp932->decode((split(/#/, $i_nam, 2))[0]);

		# $ng_nm�Őݒ肳�ꂽ�֎~�����񂪊܂܂�Ă��Ȃ����ǂ����`�F�b�N
		if($ng_nm) {
			foreach my $check_target (split(/,/, $ng_nm)) {
				# �ݒ肳�ꂽ�֎~����������ꂼ�����������ɕϊ����Ă���`�F�b�N
				if(index($utf8flagged_name, $enc_cp932->decode($check_target)) != -1) {
					$ng_flg = 1;
					last;
				}
			}
		}

		# ���͂��ꂽ�������S�ċ�����Ă��邩�ǂ����`�F�b�N
		if(!$ng_flg && @permit_name_regex) {
			# �������̐��K�\�������N���X���쐬
			my $permit_name_regex_charclass = '^[' . join('', @permit_name_regex) . ']*$';

			# ���O���œ��͂��ꂽ�������S�ċ�����Ă��邩�ǂ����`�F�b�N
			$ng_flg ||= $utf8flagged_name !~ /(?:^$|${permit_name_regex_charclass})/;
		}

		# �֎~�����񂠂邢�́A���͂�������Ă��Ȃ������������������̃G���[�\��
		if($ng_flg) {
			&error("���O���u $i_nam �v�͏������݂ł��܂���B");
		}
	}
}

#-------------------------------------------------
#  ���{��`�F�b�N
#-------------------------------------------------
sub jp_wd {
	local($sub, $com, $mat1, $mat2, $code1, $code2);
	$sub = $i_sub;
	$com = $i_com;

	if ($sub) {
		($mat1, $code1) = &jcode'getcode(*sub);
	}
	($mat2, $code2) = &jcode'getcode(*com);
	if ($code1 ne 'sjis' && $code2 ne 'sjis') {
		&error("�薼���̓R�����g�ɓ��{�ꂪ�܂܂�Ă��܂���");
	}
}

#-------------------------------------------------
#  URL���`�F�b�N
#-------------------------------------------------
sub urlnum {
	local($com) = $i_com;
	local($num) = ($com =~ s|(https?://)|$1|ig);
	if ($num > $urlnum) {
		&error("�R�����g����URL�A�h���X�͍ő�$urlnum�܂łł�");
	}
}


#-------------------------------------------------
#  ���[�����M�i���[�U�[�ԁj
#-------------------------------------------------
sub mailsend {
	# �`�F�b�N
	if (!$usermail) {
		&error("���[�U�[�Ԃ̃��[�����M�@�\\�͖����ɂȂ��Ă��܂��B");
	}

	# �����`�F�b�N
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# �񍐎�ʔ���
	# 1: �R�����g��  2: �ᔽ�X���b�h��  3: �x���X���b�h��
	my $type = exists($in{'type'}) ? int($in{'type'}) : 0;
	if ($type < 1 || $type > 3 || ($type == 1 && !exists($in{'no'}))) {
		error("�s���ȃA�N�Z�X�ł�");
	}

	# �Ώۃ��XNo����
	my $target_res_no = $in{'type'} == 1 ? int($in{'no'}) : 1;

	# ���e���e�`�F�b�N
	if ($no_wd) { &no_wd; }
	if ($i_com ne '' && $jp_wd) {
		# jp_wd�T�u���[�`����]�p
		my ($mat, $code) = &jcode'getcode(*i_com);
		if ($code ne 'sjis') {
			error('�R�����g�ɓ��{�ꂪ�܂܂�Ă��܂���');
		}
	}
	if ($urlnum > 0) { &urlnum; }
	if ($i_nam eq "") {
		if ($in_name) { &error("���O�͋L���K�{�ł�"); }
		else { $i_nam = '������'; }
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/)
	{ &error("���O�͐������L�����Ă�������"); }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/)
	{ &error("�R�����g�͐������L�����Ă�������"); }

	# ���e�L�[�`�F�b�N
	if ($regist_key_res) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			&error("���e�L�[�����͕s���ł��B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐�������͂��Ă�������");
		}

		# ���e�L�[�`�F�b�N
		# -1 : �L�[�s��v
		#  0 : �������ԃI�[�o�[
		#  1 : �L�[��v
		my ($chk) = &registkey_chk($in{'regikey'}, $in{'str_crypt'});
		if ($chk == 0) {
			&error("���e�L�[���������Ԃ𒴉߂��܂����B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐������ē��͂��Ă�������");
		} elsif ($chk == -1) {
			&error("���e�L�[���s���ł��B<p>���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐�������͂��Ă�������");
		}
	}

	# �v���C�x�[�g�u���E�W���O���[�h�ł��邩�ǂ���
	my $is_private_browsing_mode = (exists($in{'pm'}) && $in{'pm'} eq '1') ? 1 : 0;

	# CookieA�C���X�^���X������
	my $cookie_a = UniqueCookie->new($cookie_current_dirpath);

	# CookieA�ێ��`�F�b�N
	if (!$cookie_a->is_issued()) {
		error("���M�ł��܂���");
	}

	# CookieA �l�擾
	my $cookiea_value = $cookie_a->value();

	# Cookie�ɕۑ�����Ă���o�^ID���擾
	my $cuser_id = (get_cookie())[5];

	# ����ID���擾
	my $chistory_id = HistoryCookie->new()->get_history_id();

	# �z�X�g��UserAgent�𔻒肷�郆�[�U�[�ł��邩�ǂ����𔻒�
	my $judge_host_ua_flg = 1;
	foreach my $exclude_host (@ngthread_thread_list_creator_name_override_exclude_hosts) {
		if (index($host, $exclude_host) >= 0) {
			$judge_host_ua_flg = 0;
			last;
		}
	}

	# ���[�����M���ۃ��[�U�[����
	foreach my $setting_set_str (@usermail_prohibit) {
		# �ݒ蕶����𕪊�
		my @setting_set_array = @{$mu->number_of_elements_fixed_split($setting_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@setting_set_array) != 4) {
			next;
		}

		# �v���C�x�[�g���[�h����
		if ($setting_set_array[2] eq '1' && !$is_private_browsing_mode) {
			next;
		}

		# �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̐ݒ蕶����ɂ��āA�u-�v����ɒu������
		foreach my $i (0, 1) {
			$setting_set_array[$i] =~ s/^-$//;
		}

		# �z�X�g��UserAgent���ACookieA or �o�^ID or ����ID�̂����ꂩ�ň�v�������ǂ����̃t���O
		my $host_useragent_or_cookiea_userid_historyid_matched_flg;

		# �z�X�g��UserAgent�̈�v����
        my ($host_useragent_match_array_ref) =
			@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
        $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);

		# CookieA or �o�^ID or ����ID�̈�v����
		if (!$host_useragent_or_cookiea_userid_historyid_matched_flg && $setting_set_array[1] ne '') {
			my ($cookiea_userid_historyid_match_array_ref) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookiea_value, $cuser_id, $chistory_id, $setting_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
		}

		# �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v��
		# �ǂ��炩�ň�v�����Ƃ��́A�G���[�\������
		if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
			error("���M�ł��܂���");
		}
	}

	# mail.log �ǂݍ��݁E�A�����M�����E���ꃌ�X�A���񍐐�������
	my @maillog;
	open(my $maillog_fh, '+<', $mailfile) || error("Open Error: $mailfile");
	flock($maillog_fh, 2) || error("Lock Error: $mailfile");
	seek($maillog_fh, 0, 0);
	while (<$maillog_fh>) {
		chomp($_);
		my ($maillog_thread_num, $maillog_res_num, $maillog_host, $maillog_useragent,
			$maillog_cookiea, $maillog_userid, $maillog_history_id, $maillog_time) = split(/<>/, $_);
		# $usermail_time_of_continuously_send_restricting���o�߂������O�s��
		# ���O�Ɏc�����A����������s��Ȃ�
		if ($maillog_time + $usermail_time_of_continuously_send_restricting <= $time) {
			next;
		}

		# ���ꃆ�[�U�[�̏ꍇ�̂݁A����������s��
		if (($judge_host_ua_flg && $maillog_host eq $host && $maillog_useragent eq $useragent)
			|| $maillog_cookiea eq $cookiea_value
			|| ($maillog_userid ne '-' && $maillog_userid eq $cuser_id)
			|| ($maillog_history_id ne '-' && $maillog_history_id eq $chistory_id)
		) {
			# ��������
			# �A�����M�������� ($mailwait)
			# ���ꃌ�X�A���񍐐������� ($usermail_time_of_continuously_send_restricting)
			if ($maillog_time + $mailwait > $time
				|| ($maillog_thread_num == $in{'f'} && $maillog_res_num == $target_res_no)
			) {
				error("�A�����M�͂������΂炭���Ԃ������ĉ�����");
			}
		}

		# �����ɊY�����Ȃ��ꍇ�́A�c�����O�s�Ƃ��Ĕz��ɒǉ�
		push(@maillog, $_);
	}
	seek($maillog_fh, 0, 0);

	# �X���b�h���O�t�@�C���I�[�v��
	my $thread_logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(my $threadlog_fh, '<', $thread_logfile_path) || error("Open Error: $in{'f'}.cgi");
	flock($threadlog_fh, 1) || error("Lock Error: $in{'f'}.cgi");

	# �X���b�h���O�t�@�C���擪�s���擾���A�X���b�h���E���X�����擾
	my $top = <$threadlog_fh>;
	chomp($top);
	my ($thread_sub, $num_of_res) = (split(/<>/, $top))[1, 2];
	$thread_sub =~ s/\0*//g;  # �X���b�h���Ɋ܂܂�Ă���null����(\0)���폜
	if ($num_of_res == 0) {
		$num_of_res = 1;
	}

	# �R�����g�񍐂̏ꍇ�͎w�背�X�A����ȊO�̏ꍇ�́A�X���b�h�擪���X��
	# ���O�E�z�X�g���E�R�����g�ECookieA�E�o�^ID�E����ID�E�摜�A�b�v�������擾����
	my ($res_name, $res_comment, $res_host, $res_cookiea, $res_userid, $res_historyid, $res_num_of_img);
	my $res_found_flg;
	if ($type != 1 || $target_res_no <= $num_of_res) {
		while (<$threadlog_fh>) {
			chomp($_);
			my @res = split(/<>/, $_);
			if ($type != 1 || $res[0] == $target_res_no) {
				($res_name, $res_comment, $res_host, $res_userid, $res_cookiea, $res_historyid) = @res[2, 4, 6, 16, 18, 19];
				$res_num_of_img = scalar(grep { $_ !~ qr/^,/ } @res[12..14]);
				$res_found_flg = 1;
				last;
			} elsif ($res[0] > $target_res_no) {
				last;
			}
		}
	}
	if (!$res_found_flg) {
		error("�Y�����郌�X��������܂���");
	}

	# �X���b�h���O�t�@�C���N���[�Y
	close($threadlog_fh);

	# mail.log�ɋL�^���Ȃ����[�U�[�̔���
	my $maillog_record_flg = 1;
	foreach my $setting_set_str (@usermail_not_record) {
		# �ݒ蕶����𕪊�
		my @setting_set_array = @{$mu->number_of_elements_fixed_split($setting_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@setting_set_array) != 4) {
			next;
		}

		# �v���C�x�[�g���[�h����
		if ($setting_set_array[2] eq '1' && !$is_private_browsing_mode) {
			next;
		}

		# �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̐ݒ蕶����ɂ��āA�u-�v����ɒu������
		foreach my $i (0, 1) {
			$setting_set_array[$i] =~ s/^-$//;
		}

		# �z�X�g��UserAgent���ACookieA or �o�^ID or ����ID�̂����ꂩ�ň�v�������ǂ����̃t���O
		my $host_useragent_or_cookiea_userid_historyid_matched_flg;

		# �z�X�g��UserAgent�̈�v����
		if ($setting_set_array[0] ne '') {
			my ($host_useragent_match_array_ref) =
				@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);
		}

		# CookieA or �o�^ID or ����ID�̈�v����
		if (!$host_useragent_or_cookiea_userid_historyid_matched_flg && $setting_set_array[1] ne '') {
			my ($cookiea_userid_historyid_match_array_ref) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookiea_value, $cuser_id, $chistory_id, $setting_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			$host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
		}

		# �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v��
		# �ǂ��炩�ň�v�����Ƃ��́Amail.log�ɋL�^���Ȃ����[�U�[�Ƃ��ăt���O�𗧂Ă�
		if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
			$maillog_record_flg = 0;
			last;
		}
	}

	# mail.log�ɋL�^���郆�[�U�̏ꍇ�́A@maillog�Ƀ��[�����O��ǉ�����
	if ($maillog_record_flg) {
		# mail.log�L�^�̓o�^ID�E����ID���`
		my $ml_user_id = (defined($cuser_id) && $cuser_id ne '') ? $cuser_id : '-';
		my $ml_history_id = defined($chistory_id) ? $chistory_id : '-';
		# �z��ɒǉ�
		unshift(@maillog, "$in{'f'}<>$target_res_no<>$host<>$useragent<>$cookiea_value<>$ml_user_id<>$ml_history_id<>$time<>");
	}

	# �g���b�v����
	my $i_nam2 = &trip($i_nam);

	# ���[���^�C�g�����`
	my $msub;
	if ($type == 1) {
		$msub = "�ᔽ�R�����g�F$thread_sub";
	} elsif ($type == 2) {
		$msub .= "�ᔽ�X���b�h�F$thread_sub";
	} else { # elsif ($type == 3)
		$msub .= "�x���X���b�h�F$thread_sub";
	}
	if (!$maillog_record_flg) {
		# mail.log�ɋL�^���Ȃ����[�U�[�̏ꍇ�́A���[���^�C�g�������Ɂ���ǉ�
		$msub .= "��";
	}

	# �{���̉��s�E�^�O�𕜌�
	$res_comment =~ s/<br>/\n/g;
	$res_comment =~ s/&lt;/</g;
	$res_comment =~ s/&gt;/>/g;
	$res_comment =~ s/&quot;/"/g;
	$res_comment =~ s/&amp;/&/g;

	# ���[�U�[�R�����g�̉��s�E�^�O�𕜌�
	my $user_comment = $i_com;
	$user_comment =~ s/<br>/\n/g;
	$user_comment =~ s/&lt;/</g;
	$user_comment =~ s/&gt;/>/g;
	$user_comment =~ s/&quot;/"/g;
	$user_comment =~ s/&amp;/&/g;

	# ���[���{�����`
	my $mbody = "�X���b�h���F$thread_sub\n";
	if ($type == 1) {
		$mbody .= "�ᔽ�R�����gURL�F$fullscript?mode=view&no=$in{'f'}&l=$in{'no'}\n";
		$mbody .= "URL�F$fullscript?mode=view&no=$in{'f'}\n";
	} elsif ($type == 2) {
		$mbody .= "�ᔽ�X���b�hURL�F$fullscript?mode=view&no=$in{'f'}\n";
	} else { # elsif ($type == 3)
		$mbody .= "�x���X���b�hURL�F$fullscript?mode=view&no=$in{'f'}\n";
	}
	if ($type != 3 && $in{'category'} ne '-') {
		$mbody .= "��ށF$in{'category'}\n";
	}
	$mbody .= <<"EOM";

�y�񍐁z
���O�F$res_name
�z�X�g�F$res_host
CookieA�F$res_cookiea
EOM
	## �Ώۃ��X�̃��O�ɋL�^������o�^ID�E����ID�ƁA�摜�A�b�v����(1���ȏ�̏ꍇ�̂�)��{���ɒǉ�
	if ($res_userid ne '') {
		$mbody .= "�o�^ID�F$res_userid\n";
	}
	if ($res_historyid ne '') {
		$mbody .= "����ID�F$res_historyid\n";
	}
	if ($res_num_of_img > 0) {
		$mbody .= "�摜�A�b�v�F${res_num_of_img}��\n";
	}
	$mbody .= <<"EOM";
�{���F
$res_comment

�y���M�ҁz
CookieA�F$cookiea_value
EOM
	## ���M�҂��o�^ID�E����ID��ێ����Ă���ꍇ�́A���̍��ڂ�{���ɒǉ�
	if (defined($cuser_id) && $cuser_id ne '') {
		$mbody .= "�o�^ID�F$cuser_id\n";
	}
	if (defined($chistory_id)) {
		$mbody .= "����ID�F$chistory_id\n";
	}
	$mbody .= <<"EOM";
�z�X�g���F$host
UserAgent�F$useragent
EOM
	## ���M�҂��v���C�x�[�g���[�h�ő��M�����ꍇ�́A���̍��ڂ�{���ɒǉ�
	if ($is_private_browsing_mode) {
		$mbody .= "�v���C�x�[�g���[�h�F�L��\n";
	}
	$mbody .= <<"EOM";
���[�U�[�R�����g�F
$user_comment
EOM

	# �����E���o�l�E�����EX-Mailer������G���R�[�h�ɕϊ���ABase64�G���R�[�h���ꂽUTF-8��MIME�w�b�_�[�\�L�ɂ���
	my $enc_mimeheader = Encode::find_encoding('MIME-Header'); # MIME�w�b�_�[�p Encode�C���X�^���X�쐬
	my $mail_header_to = $enc_mimeheader->encode($enc_cp932->decode($usermail_to_address));
	my $mail_header_from = $enc_mimeheader->encode($enc_cp932->decode("\"$i_nam2\" <$usermail_to_address>"));
	my $mail_header_subject = $enc_mimeheader->encode($enc_cp932->decode($msub));
	my $mail_header_mailer = $enc_mimeheader->encode($enc_cp932->decode($ver));

	# ���t�w�b�_�[���쐬
	my $mail_header_date = strftime("%a, %d %b %Y %H:%M:%S %z", @localtime);

	# �{����Base64�G���R�[�h���ꂽUTF-8�ɕϊ�
	my $base64_body = encode_base64(Encode::encode_utf8($enc_cp932->decode($mbody)));

	# sendmail���M
	open(my $sendmail_ph, '|-', "$sendmail -t") || &error("���M���s");
	print $sendmail_ph <<"EOM";
To: $mail_header_to
From: $mail_header_from
Subject: $mail_header_subject
Date: $mail_header_date
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: base64
X-Mailer: $mail_header_mailer

$base64_body
EOM
	close($sendmail_ph);

	# �������b�Z�[�W
	&header;
	print <<EOM;
<br><br><div align="center">
<Table border=0 cellspacing=0 cellpadding=0 width="400">
<Tr><Td bgcolor="$col1">
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap align="center" height=60>
	<h3 style="font-size:15px">���[���𑗐M���܂���</h3>
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
EOM

	# �߂�t�H�[��
	print <<"EOM";
<table>
<tr>
  <td valign=top>
    <a href="$bbscgi"><button type="button">�f���֖߂�</button></a>
  </td>
  <td width=15></td>
  <td valign=top>
    <a href="$readcgi?mode=view&no=$in{'f'}"><button type="button">�X���b�h�֖߂�</button></a>
  </td>
</tr>
</table>
</div>
</body>
</html>
EOM

	# ���[�����O�X�V
	seek($maillog_fh, 0, 0);
	print $maillog_fh join("\n", @maillog) . "\n";
	truncate($maillog_fh, tell($maillog_fh));
	close($maillog_fh);

	exit;
}

#-------------------------------------------------
#  FAQ�����̂��߂ɎQ�Ƃ���Ă���X���b�h�ԍ����L�^
#-------------------------------------------------

sub faqcount {
# �����󂯎�� �R�����g���A�X���b�h�ԍ�
#	local($msg, $faqf) = @_;
#		&faqcount ($i_com,$in{'res'});
	local($flag,@faqs);
	local ($msg, $faqf);
	$msg = $i_com;
	$faqf= $in{'res'};
# �R�����g������A�Q�Ɛ�X���b�h�ԍ��𒊏o���Ĕz���
#	@faqs =~ /(?:$fullscript)(?:[^n\"]*)no=(\d+)/;
#	@faqs = /no=(\d+)/;
#	while ($word =~ /(.)/g){ push(@word, $1); }
	while ($msg =~ /no=(\d+)/g){ push(@faqs, $1); }

# �e�X�g�Ȃ�łƂ肠�����P��
#	$faq = $1;
#	$faq = 2;

	foreach $faq (@faqs) {
		chomp($faq);
#	if ($faq) {
# FAQ�̃J�E���g������t�@�C��
$faqfile = "./faq.log";
# �X���b�hNo<>�Q�Ƃ��Ă���X���b�hNo1,No2,No3,,,<>

			# FAQ�Ǘ��t�@�C������Y���X���b�h�����o��
			my $new_log;
			open(DAT,"+< $faqfile") || &error("Open Error: $faqfile");
			eval "flock(DAT, 2);";

			$flag=0;
			while(<FAQ>) {
				chomp($_);
				local($no,$refs) = split(/<>/);
				if ($faq == $no) {
					local(@array) = split(/\,/, $refs);
					local(@tmp);
					for (@array){$tmp[$_]=1;}
					if ($tmp[$faqf]) {
						$new_log = "$_\n" . $new_log;
					} else {
						$new_log = "$faq<>$refs,$faqf<>\n" . $new_log;
					}
				$flag++;
				} else {
					$new_log = "$_\n" . $new_log;
				}
			}

			if (!$flag) {
				$new_log = "$faq<>$faqf<>\n" . $new_log;
			}

			# ���s���Oindex�X�V
			seek(FAQ, 0, 0);
			print FAQ $new_log;
			truncate(FAQ, tell(FAQ));
			close(FAQ);
	}
}

#-------------------------------------------------
#  �X���b�h�쐬��/���X���e�����O�t�@�C�� �J�E���g�A�b�v
#-------------------------------------------------
sub regist_log_countup {
	my ($logfile) = @_;

	# ���O�t�@�C�������݂��A�ǂݏ������s���鎞�̂݃J�E���g�A�b�v����
	if(-f $logfile && -r $logfile && -w $logfile) {
		open(my $fh, '+<', $logfile) || return;
		if(flock($fh, 2)) { # ���b�N���s���͏������܂Ȃ�
			my $log;
			my $date = strftime('%Y/%m/%d', @localtime); # �����̓��t���t�H�[�}�b�g

			# �J�E���g���쐬
			my $count = 0;
			my $top = <$fh>;
			my @tops = split(/[ ��\n]/, $top);
			if(scalar(@tops) == 2 && $tops[0] eq $date && $tops[1] =~ /^\d*$/) {
				# ���O�t�@�C���̐擪�s�������Ő������t�H�[�}�b�g�������ꍇ�ɁA
				# �L�^����Ă���J�E���g���擾
				$count = $tops[1];
			} else {
				$log .= $top;
			}
			$count++; # �J�E���g�A�b�v
			$log = "$date $count��\n" . $log;

			# ���O�t�@�C���̎c��̍s��ǂݍ���
			{
				local $/ = undef;
				$log .= <$fh>;
			}

			# ���O�t�@�C���ɏ�������
			seek($fh, 0, 0);
			print $fh $log;
			truncate($fh, tell($fh));
		}
		close($fh);
	}
}

# NG�X���b�h�@�\ �X���b�h�쐬�҂̖��O�㏑�� �Ώ۔���T�u���[�`��
sub ngthread_name_override_judge {
	my ($name, $user_id, $cookie_a, $history_id, $parent_res_log_array_ref) = @_;

	# ���X���O�s�p�[�X
	# >>1�̃z�X�g�E�o�^ID�ECookieA�E����ID�����O�s����ǂݎ��
	my ($parent_res_host, $parent_res_user_id, $parent_res_cookie_a_value, $parent_res_history_id) = @{$parent_res_log_array_ref}[6,16,18,19];

	# ���O���O����
	if (grep { $_ ne '' && index($name, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_names) {
		return 0;
	}

	# �z�X�g���ꔻ��
	if (scalar(grep { $_ ne '' && index($host, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0
		&& $parent_res_host ne '' && $host eq $parent_res_host) {
		return 1;
	}

	# �o�^ID���ꔻ��
	if ($parent_res_user_id ne '' && $user_id eq $parent_res_user_id) {
		return 1;
	}

	# CookieA���ꔻ��
	if ($parent_res_cookie_a_value ne '' && $cookie_a->value() eq $parent_res_cookie_a_value) {
		return 1;
	}

	# ����ID���ꔻ��
	if ($parent_res_history_id ne '' && $history_id eq $parent_res_history_id) {
		return 1;
	}

	# ������̍��ڂɂ���v���Ȃ�����
	return 0;
}

# ���e���̖��O�̏����@�\ �Ώ۔���T�u���[�`��
sub is_remove_name_target_post {
	my ($thread_title, $raw_name, $host, $useragent, $cookie_a, $user_id, $history_id, $target_settings_array_ref) = @_;
	if (ref($target_settings_array_ref) ne 'ARRAY') {
		return;
	}

	SET_LOOP: foreach my $raw_target_set_str (@{$target_settings_array_ref}) {
		# �u:�v�ŋ�؂��Ĕz��Ƃ���
		my @target_set_array = @{$mu->number_of_elements_fixed_split($raw_target_set_str, 4, Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (scalar(@target_set_array) != 4) {
			next SET_LOOP;
		}

		# �u-�v�݂̂̏ꍇ�Ɂu�v(��)�ɒu��������
		for (my $i=0; $i<4; $i++) {
			$target_set_array[$i] =~ s/^-$//;
		}

		# �X���b�h������
		my ($title_match_array_ref) =
			@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $target_set_array[0], undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if (!defined($title_match_array_ref)) {
			# �ΏۃX���b�h���ݒ肪�Ȃ��ꍇ��A�ݒ�ɍ��v���Ȃ������ꍇ�̓Z�b�g���X�L�b�v
			next SET_LOOP;
		}

		# ���O����
		if (!defined($mu->get_matched_name_to_setting($raw_name, $target_set_array[1], Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			# �Ώۂ̖��O�̐ݒ肪�Ȃ��ꍇ��A���O����v���Ȃ������ꍇ�̓Z�b�g���X�L�b�v
			next SET_LOOP;
		}

		# �z�X�g��UserAgent�̑g�ݍ��킹����ECookieA or �o�^ID or ����ID�����
		# �ے�w��ɂ���v������s�������ǂ���
		my $is_not_match = 0;

		# �z�X�g��UserAgent�̑g�ݍ��킹����
		my @host_useragent_match = (0, -1);
		if ($target_set_array[2] ne '') {
			my ($host_useragent_match_array, undef, $not_match_flg) =
				@{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $target_set_array[2], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			@host_useragent_match = (defined($host_useragent_match_array), $not_match_flg);
			$is_not_match ||= $not_match_flg;
		}

		# CookieA or �o�^ID or ����ID����
		my @cookiea_userid_historyid_match = (0, -1);
		if ($target_set_array[3] ne '') {
			my ($cookiea_userid_historyid_match_array, $not_match_flg) =
				@{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $target_set_array[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
			@cookiea_userid_historyid_match = (defined($cookiea_userid_historyid_match_array), $not_match_flg);
			$is_not_match ||= $not_match_flg;
		}

		# ��v���� or �ے�w��ɂ��s��v����Ŕ��茋�ʂ��i��A�����Ώۂ��ǂ�������
		if ($is_not_match == 0) {
			# �ʏ�̈�v����̏ꍇ
			# (�����ꂩ�Ɉ�v�̏ꍇ)
			if (scalar(grep { ${$_}[1] == $is_not_match && ${$_}[0] } (\@host_useragent_match, \@cookiea_userid_historyid_match)) > 0) {
				return 1;
			}
		} else { # $is_not_match == 1
			# �ے�w��ɂ��s��v����̏ꍇ
			# (�S�ĕs��v�̏ꍇ)
			my @not_match_items = grep { ${$_}[1] == $is_not_match } (\@host_useragent_match, \@cookiea_userid_historyid_match);
			if (scalar(@not_match_items) > 0 && scalar(grep { ${$_}[0] } @not_match_items) == scalar(@not_match_items)) {
				return 1;
			}
		}
	}

	# ������̐ݒ�ɂ���v���Ȃ�����
	return;
}

# �������݃��O�̒u���L�^�@�\ �u������E�u���㕶����쐬�T�u���[�`��
sub replace_contents_for_post_log {
	my ($original_contents) = @_;

	# ��̏ꍇ�͈�v������s��Ȃ�
	if ($original_contents eq '') {
		return $original_contents;
	}

	# ��v����
	my @matched_str_array; # ��v�����ϊ��㕶����̔z��
	my $original_contents_array_ref_for_matching = [$original_contents]; # ��v����Ŏg�p���邽�߂̃I���W�i��������̔z�񃊃t�@�����X
	foreach my $raw_replace_set_str (@post_log_contents_replace) {
		# �����G���R�[�h�ɕϊ����A�u:�v�ŋ�؂�
		my $utf8flagged_replace_set_str = $enc_cp932->decode($raw_replace_set_str);
		my ($find_str, $replace_str) = split(/:/, $utf8flagged_replace_set_str, 2);
		if ($find_str eq '' || !defined($replace_str)) {
			# ���������񂪋󂩁A�u�������񂪒�`����Ă��Ȃ��Ƃ��̓X�L�b�v
			next;
		}

		# ��v����
		if (defined($mu->universal_match($original_contents_array_ref_for_matching, [$find_str], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
			# ��v������A�ϊ��㕶�����CP932�ɖ߂��Ĕz��ɒǉ�
			push(@matched_str_array, $enc_cp932->encode($replace_str));
		}
	}

	# �u���㕶�����Ԃ�
	if (scalar(@matched_str_array) > 0) {
		# 1�ȏ�̐ݒ�l�ƈ�v���Ă�����A�z����u;�v�Ō��������������Ԃ�
		return join(';', @matched_str_array);
	} else {
		# 1����v���Ă��Ȃ�������A�I���W�i���������Ԃ�
		return $original_contents;
	}
}

# �d�����e��������T�u���[�`��
sub is_duplicate_post {
	my ($thread_title,
		$img_upload_flg, $com, $cookie_a, $user_id, $history_id, $host,
		$lastres_com, $lastres_cookie_a, $lastres_user_id, $lastres_history_id, $lastres_host,
		$settings_array_ref) = @_;

	# ���e�{���E�ŏI���X�{����v����
	if ($com ne $lastres_com || ($img_upload_flg && $com eq '')) {
		# ��v���Ȃ��������A�摜���e������{�����Ȃ��ꍇ�́A�d�����e�ł͂Ȃ�
		return;
	}

	# CookieA or �o�^ID or ����ID or �z�X�g��v�t���O
	my $cookiea_userid_historyid_host_matched_flg;

	# ���eCookieA�E�ŏI���XCookieA��v����
	if (defined($cookie_a) && $cookie_a ne '' && $cookie_a eq $lastres_cookie_a) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# ���e�o�^ID�E�ŏI���X�o�^ID��v����
	if (!$cookiea_userid_historyid_host_matched_flg && defined($user_id) && $user_id ne '' && $user_id eq $lastres_user_id) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# ���e����ID�E�ŏI���X����ID��v����
	if (!$cookiea_userid_historyid_host_matched_flg && defined($history_id) && $history_id ne '' && $history_id eq $lastres_history_id) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# ���e�z�X�g�E�ŏI���X�z�X�g��v����
	# (@ngthread_thread_list_creator_name_override_exclude_hosts�ƍŏI���X�z�X�g�����Ԉ�v����ꍇ�͔�����s��Ȃ�)
	if (!$cookiea_userid_historyid_host_matched_flg
		&& scalar(grep { $_ ne '' && index($lastres_host, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0
		&& $host eq $lastres_host
	) {
		$cookiea_userid_historyid_host_matched_flg = 1;
	}

	# CookieA or �o�^ID or ����ID or �z�X�g�̂�����ɂ���v���Ȃ��ꍇ�́A�d�����e�ł͂Ȃ�
	if (!$cookiea_userid_historyid_host_matched_flg) {
		return;
	}

	# �X���b�h����v����
	my $normal_matched_flg;
	foreach my $settings_str (@{$settings_array_ref}) {
		my @thread_match_result =
			@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $settings_str, undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		if ($thread_match_result[1] == 1) {
			# �ے��v
			if (!defined($thread_match_result[0])) {
				# �ے�����̂����ꂩ�Ɉ�v�������߁A�d�����e�������s��Ȃ�
				return;
			}
			# �ʏ�����݂̂ōēx����
			@thread_match_result =
				@{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($thread_title, $settings_str, 1, undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
		}
		# �ʏ��v����
		$normal_matched_flg ||= defined($thread_match_result[0]);
	}

	return $normal_matched_flg;
}
