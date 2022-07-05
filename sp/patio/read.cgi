#!/usr/bin/perl

#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� patio.cgi - 2007/06/06
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���肵�܎� K0.98
# 2010/11/14 �X���ԍ��̕\�����I�v�V�����őI�ׂ�悤��
# 2010/10/19 auro_link �� >> �̏����������ɂȂ����܂܂������̂ŏC��
# 2009/12/06 auto_link �̒u��������ɊԈႢ�B
# 2009/07/01 �ߋ����O�Ŗ����I�� &mode=past �Ȃ̂Ƀt���O�������Ă��Ȃ��ƌ��s���O�Ƃ��ď������Ă���̂��C��
# 2009/07/01 $restitle=1�̂Ƃ��A�X�����\�[�g����`�F�b�N�{�b�N�X���o�Ă��Ȃ�����
# 2009/07/01 �����N��rel=nofollow�����T�C�g���̂ݍ폜����悤��
# 2009/06/23 $restitle��1�ɂ��邱�ƂŃv���r���[�@�\�𖳌��ɏo����悤�ɏC���iThanks to �O���l�j
# 2009/06/21 $t_max��$res�������ɂȂ�ƋL�����\������Ȃ����ۂւ̑Ώ��̌�����
# 2009/06/21 �ʋL���\���̃A�C�R�����ω�����悤�ɁA�܂������N������̃X���ɁB$t_max��$res�������ɂȂ�ƋL�����\������Ȃ����ۂɂƂ肠�����Ώ��i�����Ă邩�ȁj
# 2009/06/19 ���X�̃f�t�H���g�^�C�g����L���ɂ��Ă��Ă����f����Ȃ�
# 2009/06/16 �t�@�C���̃A�b�v���[�h���ł��Ȃ��̂ŁA�v���r���[���Ɏw�肷�邱�ƂɏC��
# 2009/06/15 ���X�ԍ������������Ȃ�o�O�C��
# 2009/06/02 ���X�ɂ��^�C�g���ݒ�@�\
# 2009/06/02 ���X���ł��Ȃ��Ȃ��Ă���o�O�̏C��
# 2009/06/01 ���[�U�[�ԃ��[���@�\�𖳌��ɂł���悤�ɁA�^�C�g�����ォ����͂ł���悤��
# 2009/04/07 �ߋ����O�̌Ăѕ��Ō��s���O��\������Ɖߋ����O�̂悤�ɕ\�������̂�}������@�\�̃e�X�g
# 2009/03/28 �������[�h
# 2009/03/25 rel=nofollow�̋L�q�~�X�A�L�q�R����C��
# 2009/03/14 �V�K�X���b�h�쐬�������[�h�̒ǉ��E�O���ւ̃����N�� nofollow �ǉ��B
# 2008/10/17 ���X�w��\���̃o�O�C��
# 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V
# 2008/04/15 ���[�����M�t�H�[���ւ̃����N�̃o�O�C��
# 2008/01/09 �ߋ����O�̃t���O�ɂȂ��Ă���X���́Aview�ŌĂяo���Ă��ߋ����O�Ƃ��ĕ\��
# 2007/10/27 ���X�̃��X��S�ĕ\���Ɏ��g��
# 2007/06/10 3.2�����ɏC��
#----------------------------------
#������
# $dat ���e����
#----------------------------------
BEGIN {
	# �O���t�@�C����荞��
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use List::Util;
use JSON::XS;
use HTML::Entities;
use UniqueCookie;
use HistoryCookie;
use HistoryLog;
use FirstCookie;
use ThreadCreatePostRestrict;
use Matcher::Utils;
use Matcher::Variable;
no encoding;

&parse_form;
&axscheck;

# Matcher::Utils �C���X�^���X������
# (������ Matcher::Variable �C���X�^���X�����������ăZ�b�g)
my Matcher::Utils $mu = Matcher::Utils->new(
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

# CookieA�̃C���X�^���X�����������ACookieA�̒l�ƌ����_�ł̔��s�󋵂��擾 (���s�͂��Ȃ�)
my $cookie_a_instance = UniqueCookie->new($cookie_current_dirpath);
my ($cookie_a, $is_cookie_a_issued) = ($cookie_a_instance->value(), $cookie_a_instance->is_issued());

# Cookie�ɕۑ�����Ă���o�^ID���擾
my $cuser_id = do {
	my @cookies = get_cookie();
	$cookies[5] || '';
};

# ����ID���擾
my $chistory_id = do {
	my $instance = HistoryCookie->new();
	$instance->get_history_id();
};

# ����Cookie�C���X�^���X������
my $first_cookie = FirstCookie->new(
	$mu,
	$firstpost_restrict_settings_filepath,
	$time, $host, $useragent, $cookie_a_instance, $cuser_id, $chistory_id, 0,
	$cookie_current_dirpath, \@firstpost_restrict_exempt
);

# �V�K�X���b�h�쐬/���e�v���r���[�ł́A���񏑂����݂܂ł̎��Ԑ����@�\�̔�����s��
if ($mode eq "form" || $mode eq "resview" || $mode eq "preview") {
	$first_cookie->judge_and_update_cookie(FirstCookie::THREAD_CREATE, undef);
}

# �����̓��e��ڗ�������@�\ �L����Ԏ擾
my $highlight_name_in_own_post = get_highlight_name_on_own_post();

# ���[�U�����\���@�\ �F���E�J���[�R�[�h��`
my @highlight_userinfo_color_name_code = (
    ['��', '#ff7f50'], ['��', '#bfecbf'], ['�I�����W', '#ffa500'], ['��', '#87cefa'], ['��', '#ca95ff'],
    ['�s���N', '#ffb6c1'], ['����', '#bdb76b'], ['����', '#e0f800'], ['�Ԓ�', '#850000'], ['�Z��', '#228b22']
);

if ($mode eq "form") { &form; }
elsif ($mode eq "resview") { &resview; }
elsif ($mode eq "preview") { &preview; }
elsif ($mode eq "past") { &past; }
elsif ($mode eq "view2") { &view2; }
elsif ($mode eq "mail") { &mailform; }
elsif ($mode eq "sethighlightname") { set_highlight_name_on_own_post(); }
elsif ($mode eq "setngword") { set_ngword_cookie(); }
elsif ($mode eq "setchainng") { set_chain_ng(); }
elsif ($mode eq "clearngname") { clear_ngname(); }
elsif ($mode eq "clearngid") { clear_ngid(); }

# �\�����e����@�\�̕��򔻒�Ŏg�p���܂�
my @decoded_contents_branching_keyword = do {
	my @tmp_decoded_array;
	foreach my $encoded_keyword (@contents_branching_keyword) {
		push(@tmp_decoded_array, $enc_cp932->decode($encoded_keyword)); # �Ώە����������G���R�[�h�ɕϊ�
	}
	(@tmp_decoded_array);
};

&view;

#-------------------------------------------------
#  �X���{��
#-------------------------------------------------
sub view {
	local($no,$sub,$res,$key,$no2,$nam,$eml,$com,$dat,$ho,$pw,$url,%resCountPerPoster,$cut_nam,$is_branching_contents,
		$log_user_id,$log_cookie_a,$log_history_id,$log_useragent,$log_is_private_browsing_mode,$log_first_access_datetime);
	local($job) = @_;

	# �A���[�����`
	local($alarm) = int ($m_max * 0.9);

	# �X�}�C���A�C�R����`
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
	}

	# �����`�F�b�N
	$in{'no'} =~ s/\D//g;

	# �X���b�h���O�ꊇ�ǂݍ���
	my @log;
	{
		my $logfile_path = get_logfolder_path($in{'no'}) . "/$in{'no'}.cgi";
		open(my $log_fh, $logfile_path) || &error("Open Error: $in{'no'}.cgi");
		flock($log_fh, 1) || &error("Lock Error: $in{'no'}.cgi");
		while(<$log_fh>) {
			$_ =~ s/(?:\r\n|\r|\n)$//;
			push(@log, [split(/<>/)]);
		}
		close($log_fh);
	}

	# �X���b�h���ǂݍ���
	($no,$sub,$res,$key) = @{$log[0]};
	$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
	my $thread_title = $sub; # �{���̃X���b�h�^�C�g�����L��
	my $thread_no = $no; # �����p�ɃX���b�h�ԍ���ʂɋL��
	judge_branch_contents($sub); # �\�����e����@�\ �X���b�h�^�C�g������

	# �J�e�S�������������X���b�h�^�C�g�����擾
	my $category_removed_thread_title = $enc_cp932->decode($thread_title);
	foreach my $conv_set_str (@category_convert) {
		my $decoded_conv_set_str = $enc_cp932->decode($conv_set_str);
		my ($keyword) = split(/:/, $decoded_conv_set_str, 2);
		if ($keyword eq '') {
			next;
		}
		local $1; # �}�b�`�ϐ��̃X�R�[�v������
		my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
		if ($category_removed_thread_title =~ /$capture_regex/) {
			# �X���b�h�����J�e�S���������������̂Œu������
			$category_removed_thread_title = $1;
			last;
		}
	}
	if (Encode::is_utf8($category_removed_thread_title)) {
		$category_removed_thread_title = $enc_cp932->encode($category_removed_thread_title);
	}

    # �X���b�h�{�������@�\
    {
		# ���t�ɂ�鏜�O�̔���̂���
		# CookieA���s���� ���l�\�����쐬 (���݂�CookieA���s�`���Ɍ���)
		my $cookie_a_issue_datetime_num;
		if ($is_cookie_a_issued && $cookie_a =~ /^(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[0-1]))_.._((?:[01]\d|2[0-3])[0-5]\d)$/) {
			$cookie_a_issue_datetime_num = int("$1$2");
		}

		# ���t�ɂ�鏜�O�̔���̂���
		# CookieA�̕�������\�ߎ擾
		my $cookie_a_length;
		if ($is_cookie_a_issued) {
			$cookie_a_length = length($cookie_a);
		}

        # ������{
        my $is_thread_browsing_restrict_user = 0;
        my $disable_setting_flg_char = $enc_cp932->decode('��');
        my $utf8_flagged_category_removed_thread_title = $enc_cp932->decode($category_removed_thread_title);
        foreach my $setting_set_str (@thread_browsing_restrict_user) {
            my @setting_set_array = split(/:/, $enc_cp932->decode($setting_set_str), -1);
            if (scalar(@setting_set_array) > 8) {
				@setting_set_array = (
					@setting_set_array[0 .. 4],
					join(':', @setting_set_array[5 .. $#setting_set_array - 2]),
					@setting_set_array[$#setting_set_array - 1 .. $#setting_set_array]
				);
			} elsif (scalar(@setting_set_array) < 8) {
				next;
			}

            # �ݒ薳������
            if ($setting_set_array[0] eq $disable_setting_flg_char) {
                next;
            }

            # CookieA�̗L������
            if ($setting_set_array[4] eq '1' && $is_cookie_a_issued) {
                # 1���Z�b�g����Ă���ꍇ�́ACookieA�����s���[�U�[�݂̂�����Ώۂ̂��߁A
                # CookieA�����݂��郆�[�U�[�͑ΏۊO
                next;
            }

            # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�ɂ���
            # �u-�v�݂̂̏ꍇ�Ɂu�v(��)�ɒu��������
            foreach my $i (2, 3, 6) {
                if ($setting_set_array[$i] eq '-') {
                    $setting_set_array[$i] = '';
                }
            }

            # �X���b�h�����A
            # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̗�������l�̏ꍇ�̓X�L�b�v
            if ($setting_set_array[1] eq ''
                || ($setting_set_array[2] eq '' && $setting_set_array[3] eq '')) {
                next;
            }

            # �X���b�h������
            if (!defined($mu->universal_match([$utf8_flagged_category_removed_thread_title], [$setting_set_array[1]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # ��v���Ȃ��Ƃ��͎��̃��[�v��
                next;
            }

            # �z�X�g��UserAgent�̑g�ݍ��킹����
            if ($setting_set_array[2] ne '') {
                my ($host_useragent_match_array) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[2], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array)) {
                    $is_thread_browsing_restrict_user = 1;
                }
            }

            # CookieA or �o�^ID or ����ID����
            if (!$is_thread_browsing_restrict_user && $setting_set_array[3] ne '') {
                my ($cookiea_userid_historyid_match_array) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $cuser_id, $chistory_id, $setting_set_array[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array)) {
                    $is_thread_browsing_restrict_user = 1;
                }
            }

			# ���t�ɂ�鏜�O����
			if ($is_thread_browsing_restrict_user && $is_cookie_a_issued && $setting_set_array[5] ne '') {
				# �ݒ�l�̓�����r���l�\���z����쐬
				my @reference_datetime_num_array = map {
					$_ =~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/ ? int("$1$2$3$4$5") : ();
				} split(/,/, $setting_set_array[5]);

				# CookieA�̕������ŏ����𕪊�
				if ($cookie_a_length == 14) {
					foreach my $reference_datetime_num (@reference_datetime_num_array) {
						# CookieA���s�������ݒ�l���������ł���ꍇ�͏��O�Ώ�
						if ($cookie_a_issue_datetime_num < $reference_datetime_num) {
							$is_thread_browsing_restrict_user = undef;
							last;
						}
					}
				} elsif ($cookie_a_length == 12 && scalar(@reference_datetime_num_array) > 0) {
					# CookieA�̒l��12���̏ꍇ�͂��ׂď��O�Ώ�
					$is_thread_browsing_restrict_user = undef;
				}
			}

			# CookieA or �o�^ID or ����ID�̏��O����
			if ($is_thread_browsing_restrict_user && $setting_set_array[6] ne '') {
				my ($cookiea_userid_historyid_match_array) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $cuser_id, $chistory_id, $setting_set_array[6], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
				if (defined($cookiea_userid_historyid_match_array)) {
					$is_thread_browsing_restrict_user = undef;
				}
			}

			# ���胋�[�v�p������
			if ($is_thread_browsing_restrict_user) {
				last;
			}
        }
        # �X���b�h�{�������Ώۃ��[�U�[�̏ꍇ�̓��_�C���N�g
        if ($is_thread_browsing_restrict_user) {
            print "Location: $thread_browsing_restrict_redirect_url\n\n";
            exit(0);
        }
    }

	# ���񏑂����݂܂ł̎��Ԑ����@�\ ����
	$first_cookie->judge_and_update_cookie(FirstCookie::RESPONSE, $category_removed_thread_title);

	# ���[�U�����\���@�\�EUserAgent�̋����\���@�\ ���O�t�@�C���ǂݍ���
	my %highlight_userinfo_colorindex_hash = {
		'cookie_a'   => {},
		'history_id' => {},
		'host'       => {},
		'user_id'    => {}
	};
	my @highlight_ua_setting_hashref_array;
	if (-s $highlight_userinfo_log_path >= 3) { # 3�o�C�g�����̓p�[�X�̕K�v�Ȃ�
		# ���O�t�@�C���I�[�v���E�ǂݍ���
		open(my $json_log_fh, '<', $highlight_userinfo_log_path) || error("Open Error: $highlight_userinfo_log_path");
		flock($json_log_fh, 1) || error("Lock Error: $highlight_userinfo_log_path");
		seek($json_log_fh, 0, 0);
		local $/;
		my $json_log_contents = <$json_log_fh>;
		close($json_log_fh);

		# JSON�p�[�X
		# �p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A���e���Ȃ��������̂Ƃ��Ď�舵��
		my @load_hightlight_array;
		eval {
			my $json_serializer = JSON::XS->new();
			my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
			if (ref($json_parsed_ref) eq 'ARRAY') {
				@load_hightlight_array = @{$json_parsed_ref};
			}
		};

		foreach my $highlight_hashref (@load_hightlight_array) {
			# �l���n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
			if (ref($highlight_hashref) ne 'HASH') {
				next;
			}

			# �ُ�ݒ�l�̓X�L�b�v
			if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
				|| !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1 || $highlight_hashref->{color} > scalar(@highlight_userinfo_color_name_code)) {
				next;
			}

			# �����\���^�C�v���擾
			# (�Z�b�g����Ă��Ȃ��ꍇ�A���[�U�����\���Ƃ݂Ȃ�)
			my $type = exists($highlight_hashref->{type}) ? $highlight_hashref->{type} : 1;

			# �����\���^�C�v�ʂɏ���
			if ($type == 1) {
				## ���[�U�����\�� ##
				# �ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
				if (($highlight_hashref->{time} + $highlight_userinfo_hold_hour * 3600) <= $time) {
					next;
				}

				# ���ڕʂ�Color�C���f�b�N�X���Z�b�g
				foreach my $item_name ('cookie_a', 'history_id', 'host', 'user_id') {
					if (exists($highlight_hashref->{$item_name}) && $highlight_hashref->{$item_name} ne '') {
						$highlight_userinfo_colorindex_hash{$item_name}->{$highlight_hashref->{$item_name}} = int($highlight_hashref->{color}) - 1;
					}
				}
			} elsif ($type == 2) {
				## UserAgent�̋����\�� ##
				# Color�C���f�b�N�X�E�z�X�g�EUserAgent�E���Ԃɂ��ݒ�L���t���O�̃n�b�V�����t�@�����X�Ƃ��A�z��ɒǉ�
				my $add_hashref = {
					color      => int($highlight_hashref->{color}) - 1,
					host       => $highlight_hashref->{host},
					useragent  => $highlight_hashref->{useragent},
					valid_flag => ($highlight_hashref->{time} + $highlight_ua_hold_hour * 3600) > $time
				};
				push(@highlight_ua_setting_hashref_array, $add_hashref);
			}
		}
	}

	if ($key eq '-1') {$job = "past";}
#	elsif ($key ne '1') {$job = "";}
	elsif ($mode ne 'past') {$job = "";}

	# �ߋ����O
	if ($job eq "past") {
		$bbsback = "mode=past";
		$guid = "<a href=\"$readcgi?mode=past\">�ߋ����O</a> &gt; �X���b�h";

	# ���s���O
	} else {
		$bbsback = "";
		$guid = "�X���b�h";
	}

	# �e���X�ǂݍ���
	($no2, undef, $nam, $eml, $com, $dat, $ho, $pw, $url, $mvw, $myid, $tim, $upl{1}, $upl{2}, $upl{3}, $idcrypt, $log_user_id, undef,
		$log_cookie_a, $log_history_id, $log_useragent, $log_is_private_browsing_mode, $log_first_access_datetime,
		$upl{4}, $upl{5}, $upl{6}) = @{$log[1]};

	# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\�̃X���b�h�쐬�҂̏��O�@�\
	# >>1�� �z�X�g, URL��, �o�^ID, CookieA, ����ID ���擾
	my %first_res;
	{
		(my $valid_history_id = $log_history_id) =~ s/\@$//;
		%first_res = (
			'host'       => $ho,
			'url'        => $url,
			'user_id'    => $log_user_id,
			'cookie_a'   => $log_cookie_a,
			'history_id' => $valid_history_id,
		);
	}

	# ID�����e���J�E���g�@�\ �e���X���e��ID���J�E���g
	$resCountPerPoster{$idcrypt} = [$no2];

	# NG�l�[���K�p���X���O���J�b�g�\���@�\
	($nam, $cut_nam) = &cut_name($nam);

	$com = &auto_link($com, $no);

	# �\�����e����@�\ �e���X����
	judge_branch_contents($log[1]);

	# �^�C�g���ɃX���ԍ�������
	if ($showthreadno) {
		$sub="[$in{'no'}] ".$sub;
	}

	# �A�C�R����`
	if ($job ne "past" && $key eq '0') { $icon = 'fold3.gif'; }
	elsif ($job ne "past" && $key eq '4') { $icon = 'fold3.gif'; }
	elsif ($job ne "past" && $key eq '3') { $icon = 'faq.gif'; }
	elsif ($job ne "past" && $key eq '2') { $icon = 'look.gif'; }
	elsif ($job ne "past" && $res >= $alarm) { $icon = 'fold5.gif'; }
	elsif (time < $tim + $hot) { $icon = 'fold1.gif'; }
	else { $icon = 'fold1.gif'; }

	# �w�b�_
	if ($job eq "past") {
		&header($sub);
	} else {
		&header($sub, "js");
		if ($key eq '0') {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">�@�@�@�@�@<img src=\"$imgurl/alarm.gif\"> ";
			print "���̃X����<b>���b�N</b>����Ă��܂��B";
			print "�L���̉{���݂̂ƂȂ�܂��B</td></tr></table>\n";

		} elsif ($key == 2) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">�@�@�@�@�@<img src=\"$imgurl/alarm.gif\"> ";
			print "���̃X����<b>�Ǘ��l����̃��b�Z�[�W</b>�ł��B";
			print "</td></tr></table>\n";

		} elsif ($key == 3) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">�@�@�@�@�@<img src=\"$imgurl/alarm.gif\"> ";
			print "���̃X����<b>����</b>�ł��B";
			print "</td></tr></table>\n";

		} elsif ($key eq '4') {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">�@�@�@�@�@<img src=\"$imgurl/alarm.gif\"> ";
#			print "���̃X����<b>�Ǘ��l�ɂ�胍�b�N</b>����Ă��܂��B";
			print "<b>���b�N</b>����Ă��܂��B";
			print "</td></tr></table>\n";

		} elsif ($m_max <= $res) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">�@�@�@�@�@<img src=\"$imgurl/alarm.gif\"> ";
			print "�ԐM�L������<b>$res</b>������܂��B";
			print "����ȏ�̏������݂͂ł��܂���B";
			print "</td></tr></table>\n";
			$key = 0; # �ȍ~���{����p���[�h�Ƃ��ď����B

		} elsif ($alarm <= $res) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\"><img src=\"$imgurl/alarm.gif\"> ";
			print "�ԐM�L������<b>$res</b>������܂��B";
			print "<b>$m_max</b>���𒴂���Ə������݂��ł��Ȃ��Ȃ�܂��B";
			print "</td></tr></table>\n";
		}
	}

	print <<"EOM";



<style type="text/css">


.hoge{
	font-size:13px !important;
	border-top:1px solid #999999;
	padding-top:10px;
	padding-left:3px;
	padding-bottom:3px;
	color:#666666;
}
.comment{
	padding-bottom:20px;
	padding-left:15px;
}
.hi_sanshou{
	background-color:#dbf4db;
	padding:0px 10px;
}
.res_poster_id{
	cursor: pointer;
}
.hatugen_red{
	color:#bb0000;
}
.hatugen_blue{
	color:#0000ff;
}
.readup_here, .readup_here_op_result {
    display: none;
}

\#modale {
	position: fixed;
	width: 100%;
	height: 100%;
	display: none;
	cursor: pointer;
	-webkit-tap-highlight-color: rgba(0,0,0,0);
}

.modal {
  overflow: hidden;
  position: absolute;
  padding: 10px;
  width: 478px;
  background: #7de5f3;
  display: none;
  border:1px solid #333;
  z-index: 1;
  transform: translateY(0px);
}

.modal img.close {
  cursor: pointer;
  float: right;
}

.modal dl.hoge{
  border: none;
  margin: 0;
}

</style>


</head>

<body>
<div id="modale"></div>
<div id="modal"></div>


<div id="container">

<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />



<script src="./jquery.anchors.js" type="text/javascript"></script>


<script type="text/javascript"><!--
\$\(document).ready( function() {
    \$\(".scroll").scrollAnchors();
    //prettyPrint();
});
// --></script>
<script type="text/javascript">
function dofocus() {
    var element = document.getElementById("fokasuidou");
    element.focus(); // �J�[�\�������킹��
}
</script>
<div id="wrapper-main">
<div id="wrapper-main-in">
<div class="crumbs">
<a href="$home">home</a> &gt; <a href="$bbscgi?">$bbsname</a>
</div>


EOM

	# ���X�ǂݍ��ݔ͈͌���
	if ($key == 2) {
		# �Ǘ��l���b�Z�[�W�̎��̓��X��S�ĕ\������
		$l = "$no2-";
	}
	my $all_flg = ($l eq "$no2-"); # ���X�S�\���w��̎��̓t���O�𗧂Ă�
	my ($res_range_from, $res_range_to) = split(/-/, $l); # -�ŕ������ă��X�͈͂�����
	if ($l !~ /\-/) {
		# �͈͎w���'-'���Ȃ��ꍇ��1�̃��X��\��
		$res_range_to = $res_range_from;
	}
	if (!$res_range_from || $res_range_from < $no2) {
		# ���X�͈͂̎n�߂̎w�肪�Ȃ��ꍇ��A$no2(�ŏ��̃��XNo)�����̃��XNo���w�肳�ꂽ���́A
		# �ŏ��̃��X�����X�͈͎n�߂Ƃ���
		$res_range_from = $no2;

		# ���X�S�\���t���O�ă`�F�b�N
		$all_flg ||= ($l =~ /^\d+-$/);
	}
	if (!$res_range_to || $res_range_to > $res) {
		# ���X�͈͂̏I���̎w�肪�Ȃ��ꍇ��A�ő僌�XNo���傫���l���w�肳�ꂽ����
		# �ő僌�XNo�����X�͈͏I���Ƃ���
		$res_range_to = $res;
	}
	if ($res_range_from > $res_range_to) {
		# $l1(���X�͈͎n��)���A$l2(���X�͈͏I���)�����������ꍇ
		# ���ꂼ�����ւ��Đ������͈͂ɂȂ�悤�C��
		($res_range_to, $res_range_from) = ($res_range_from, $res_range_to);
	}

	# ���X�ǂݍ��ݔ͈͓��̃��X���O�z��ƂȂ�悤�t�B���^�����O
	@log = grep { (${$_}[0] >= $res_range_from && ${$_}[0] <= $res_range_to) || ${$_}[0] == $no2; } @log[1..$#log];

	# �y�[�W���v�Z
	my $page_cnt = int((scalar(@log) - 1) / $t_max);
	my $remainder_res_cnt = (scalar(@log) - 1) % $t_max;
	if (scalar(@log) == 1 || $remainder_res_cnt > 0) {
		# 1���X�ڂ݂̂̕\���A�������́A$t_max�Ŋ���؂�Ȃ����X��������Ƃ��́A
		# �y�[�W����1���₷
		$page_cnt++;
	}

	# �y�[�W�ԍ�����
	$p = int($p) || 1;
	if ($p <= 0) {
		$p = 1;
	} elsif ($p > $page_cnt) {
		$p = $page_cnt;
	}

	# �S���X�\���ł͂Ȃ��A���A�q���X���O��2�ȏ゠�鎞�́A
	# ���X�\���͈͂̃��O�z��ƂȂ�悤�A�z����\�[�g���ăt�B���^�����O����
	if (!$all_flg && (scalar(@log) - 1) > 1) {
		# $t_max���X���Ƃɕ\���u���b�N�Ƃ��Ă��̃C���f�b�N�X�ō~���\�[�g��(������$remainder_res_cnt�ȉ��̃��X�C���f�b�N�X�͏���)�A
		# �܂��A�\���u���b�N���̃��X�̓��X�C���f�b�N�X���Ƃɏ����\�[�g�Ƃ���A���O�z��\�[�g�p�C���f�b�N�X�z����쐬
		my @sort_indexes =	sort {
			$b > $remainder_res_cnt <=> $a > $remainder_res_cnt
				|| ($b > $remainder_res_cnt && $a > $remainder_res_cnt ? (int(($b - $remainder_res_cnt - 1) / $t_max)) <=> (int(($a - $remainder_res_cnt - 1) / $t_max)) : 0)
				|| $a <=> $b
		} reverse(1..$#log);

		# �\�[�g�p�C���f�b�N�X�z���
		# �y�[�W�ԍ��ɏ]���A���X�\���͈͕����݂̗̂v�f�ƂȂ�悤�t�B���^�����O
		my $from_index = ($p - 1) * $t_max; # ���X�\���͈͎n�� �C���f�b�N�X
		my $to_index = $p * $t_max - 1; # ���X�\���͈͏I��� �C���f�b�N�X
		if ($to_index > $#sort_indexes) {
			# �ő�C���f�b�N�X�𒴂���$to_index�ɂȂ��Ă��܂����Ƃ�h�����߁A�����ꂩ�����������̗p����
			$to_index = $#sort_indexes;
		}
		@sort_indexes = @sort_indexes[$from_index..$to_index];

		# ���O�z����\�[�g�E�t�B���^�����O�p�C���f�b�N�X�z��Ń\�[�g
		# (�������擪��1���X�Ƃ��邽�߁A���0������)
		@log = @log[0, @sort_indexes];
	}

	# �q���X�\���͈͂ŗ\�ߏ������s���K�v������@�\�̃��[�v����
	foreach my $res_log_array_ref (@log[1..$#log]) {
		# ID�����e���J�E���g�@�\ �\���͈͓� �q���X�̓���ID�ɂ�铊�e���J�E���g
		my ($res_no, $id) = @{$res_log_array_ref}[0, 15];
		if (exists($resCountPerPoster{$id})) {
			push(@{$resCountPerPoster{$id}}, $res_no);
		} else {
			$resCountPerPoster{$id} = [$res_no];
		}

		# �\�����e����@�\ �q���X����
		judge_branch_contents($res_log_array_ref);
	}

	# �y�[�W�J�z�{�^��
	if ($key != 2) {
		print pagelink($thread_no, $page_cnt, $all_flg);
	}

	# �X���b�h�ۑ��t�H���_�ԍ��擾
	my $thread_savefolder_number = get_logfolder_number($in{'no'});
	my $thread_savefolder_html = defined($thread_savefolder_number) ? $thread_savefolder_number : '��������';

	print <<"EOM";
<!-- google_ad_section_start -->
<h1 class="thread">$sub &nbsp;&nbsp; �t�H���_ : $thread_savefolder_html</h1>
EOM
	# �\�����e����@�\ �X���b�h�^�C�g���\������
	if ($is_branching_contents) {
		# �\���͈͂̃��X�ɐݒ肵�������񂪊܂܂�Ă��邩�A
		# �摜�`�F�b�N�L�����́A�摜���A�b�v����Ă���ꍇ
		print "<h2>�\\��1_YES</h2>\n";
	} else {
		# ����ȊO�̏ꍇ
		print "<h2>�\\��1_NO</h2>\n";
	}

	print <<"EOM";
<div class="main">
<div id="d1">
<dl class=\"hoge\"><dt>
EOM



	# �����e�{�^��
#	if ($job ne "past") {
#		print "<span class=\"mente\"></span> 1 ���O�F\n";
#	}
		print "<span class=\"num\"><a onclick=\"dofocus()\" href=\"javascript:MyFace('>>$no2\\n')\" title=\">>$no2\">$no2&nbsp;�F</a></span>\n";


	print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam$cut_nam</span> <span class=\"ng_hide\">���e���F$dat";

# ID��\��
	if($idkey && $idcrypt) {
		print " <span class=\"res_poster_id\">ID: $idcrypt";
		# ID�����e���J�E���g�@�\ ���e�����o��
		my $resCount = @{$resCountPerPoster{$idcrypt}};
		if ($resCount > 4) {
			# Binary Search
			my ($low, $high) = (0, $resCount);
			while($low < $high) {
				my $cursor = int(($high-$low)/2 + $low);
				if($resCountPerPoster{$idcrypt}->[$cursor] < $no) {
					$low = $cursor + 1;
				} else {
					$high = $cursor;
				}
			}
			print " <span class=\"hatugen_red\">[1/$resCount]</span>";
		} elsif ($resCount > 1) {
			# Binary Search
			my ($low, $high) = (0, $resCount);
			while($low < $high) {
				my $cursor = int(($high-$low)/2 + $low);
				if($resCountPerPoster{$idcrypt}->[$cursor] < $no) {
					$low = $cursor + 1;
				} else {
					$high = $cursor;
				}
			}
			print " <span class=\"hatugen_blue\">[1/$resCount]</span>";
		}
		print "</span></span>";
	} else {
		print "</span>";
	}

	# �o�^ID���o��
	if ($webprotect_auth_new && $log_user_id ne '') {
		# ���[�U�����\���@�\
		if (exists($highlight_userinfo_colorindex_hash{user_id}->{$log_user_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{user_id}->{$log_user_id}]}[1];
			print " �o�^ID:<span class=\"user_id\"><span style=\"background-color:$color_code\">$log_user_id</span></span>";
		} else {
			print " �o�^ID:<span class=\"user_id\">$log_user_id</span>";
		}
	}

	# ����ID���o��
	if ($log_history_id ne '') {
		# ���[�U�����\���@�\
		# (����ID�ɖ�����@���܂܂�Ă���ꍇ�͏����Ă��猟������)
		(my $find_history_id = $log_history_id) =~ s/\@$//;
		if (exists($highlight_userinfo_colorindex_hash{history_id}->{$find_history_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{history_id}->{$find_history_id}]}[1];
			print " ����ID:<span style=\"background-color:$color_code\">$log_history_id</span>";
		} else {
			print " ����ID:$log_history_id";
		}
	}

	# ���j�[�NCookieA���o��
	if ($log_cookie_a ne '') {
		# ���[�U�����\���@�\
		if (exists($highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a}]}[1];
			print " CookieA:<span style=\"background-color:$color_code\">$log_cookie_a</span>";
		} else {
			print " CookieA:$log_cookie_a";
		}
	}

    # �z�X�g���o��
	## ���[�U�����\���@�\
	if (exists($highlight_userinfo_colorindex_hash{host}->{$ho})) {
		my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{host}->{$ho}]}[1];
		print " �z�X�g:<span style=\"background-color:$color_code\">$ho</span>";
	} else {
		print " �z�X�g:$ho";
	}

	# UserAgent���o��
	if ($log_useragent ne '') {
		# UserAgent�̋����\���@�\
		my $color_code;
		foreach my $setting_hashref (@highlight_ua_setting_hashref_array) {
			if (!$setting_hashref->{valid_flag}) {
				# ���Ԃ��o�߂��Ė����̐ݒ���X�L�b�v
				next;
			}
			my $target_host = $setting_hashref->{host};
			my $target_useragent = $setting_hashref->{useragent};
			my $color_index = $setting_hashref->{color};

			# ��v����
			if (defined(${$mu->get_matched_host_useragent_and_whether_its_not_match($ho, $log_useragent, "$target_host<>$target_useragent", undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)}[0])) {
				$color_code = ${$highlight_userinfo_color_name_code[$color_index]}[1];
				last; # �z��̐擪���猟�����A�ŏ��Ɉ�v�����ݒ�̐F���g�p����
			}
		}

		if (defined($color_code)) {
			print " UA:<span style=\"background-color:$color_code\">$log_useragent</span>";
		} else {
			print " UA:$log_useragent";
		}
	}

	# �v���C�x�[�g���[�h���L���ł���Ώo��
	if ($log_is_private_browsing_mode) {
		print ' �v���C�x�[�g���[�h:�L��';
	}

	# ����A�N�Z�X���Ԃ��L�^����Ă���ꍇ�͏o��
	if ($log_first_access_datetime ne '') {
		print " ����A�N�Z�X����:$log_first_access_datetime";
	}

	# �摜��MD5���o��
	foreach my $i (1 .. 6) {
		my ($image_orig_md5, $image_conv_md5) = (split(/,/, $upl{$i}))[6, 7];
		next if ($image_orig_md5 eq '');

		# �ϊ��OMD5���o��
		print " �摜$i:$image_orig_md5";

		# �ϊ���MD5���L�^����Ă���ꍇ�͑����ďo��
		if ($image_conv_md5 ne '') {
			print ",$image_conv_md5";
		}
	}

	# �uNG�l�[���o�^�v��\��(�uNG�l�[�������v�\����Javascript�ɂ���ăy�[�W���[�h��ɓ��I�ɍs����)
	if($ngname) {
		print " <a href=\"#\" class=\"ngname_toggle ng_toggle\">NG�l�[���o�^</a>";
	}

	# �uNGID�o�^�v��\��(�uNGID�����v�\����Javascript�ɂ���ăy�[�W���[�h��ɓ��I�ɍs����)
	if($idkey && $idcrypt && $ngid) {
		print " <a href=\"#\" class=\"ngid_toggle ng_toggle\">NGID�o�^</a>";
	}

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}




print <<"EOM";

EOM

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}

# ID��\��
	if($idkey && $idcrypt) { print ""; }

			print "</dt></dl>\n";


# ���[�����M�t�H�[���ւ̃����N
	print <<"EOM";
EOM


#���O��ϊ�
#	�}�b�`����������̑O����擾($`, $')
#	http://www.perlplus.jp/regular/ref/index2.html

if ($nam =~ /��.*/){
#  print "<br>�O�̕��� : $`\n<br>";
#�}�b�`�������������
  $nam = $`;
#  print "�}�b�`���������� : $&\n<br>";
#  print "��̕��� : $'\n<br>";
}
# ���[�����M�t�H�[���ւ̃����N End


		if ($url) {
			print "<dt>�Q�ƁF <a href=\"$url\" target=\"_blank\" rel=\"nofollow\">$url</a></dt>\n";
		}

		# �R�����g�o��
		print "\n<div class=\"comment\">$com</div>\n";

		# �摜�o��
		my ($dd_flg, @img_filename);
		foreach my $i (1 .. 6) {
			my ($img_folder_number, $ex, $w, $h, $thumb_w, $thumb_h) = split(/,/, $upl{$i});
			next if (!$ex);

			if (!$dd_flg) {
				print "<div class=\"comment-img\">";
				$dd_flg++;
			}

			if ($in{'noimage'}) {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			} elsif (defined($imgex{$ex})) {
#			if (defined($imgex{$ex})) {
				my $thumb_path, $width, $height;
				if($thumbnail && -f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
					# �T���l�C���摜�@�\���L�����T���l�C���摜�t�@�C�������݂��鎞
					($width, $height) = &resize($thumb_w, $thumb_h);
					$thumb_path = "$thumburl/$img_folder_number/$tim-${i}_s.jpg";
				} else {
					# �I���W�i���摜���k�����ăT���l�C���摜�\������ꍇ
					($width, $height) = &resize($w, $h);
					$thumb_path = "$uplurl/$img_folder_number/$tim-$i$ex";
				}
				# �T���l�C���摜��\���ł��鎞
				if($thumb_path && $width > 0 && $height > 0) {
					# �T���l�C���摜����уI���W�i���摜�ւ̃����N HTML�o��
					print "<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\"><img src=\"$thumb_path\" align=\"top\" border=\"0\" width=\"$width\" height=\"$height\" hspace=\"3\" vspace=\"5\"></a>\n";
					# �I���W�i���摜�t�@�C�����擾
					push(@img_filename, "�� $img_filename_prefix$img_folder_number/$tim-$i$ex ��");
				}
			} else {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			}
		}

		# �摜�t�@�C�����\��
		if (scalar(@img_filename) > 0) { print "<br><br>\n"; }
		print join("<br>\n", @img_filename) . "\n";
		if ($dd_flg) { print "</div>\n"; }

		# �X���b�h��ʂ��烆�[�U�𐧌�����@�\
		print "<div>\n" . create_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
		print "<div>\n" . create_restrict_user_by_time_range_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# �X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
		print "<div>\n" . create_in_thread_only_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

        # ���[�U�����\���@�\
        print "<br><div>\n" . create_highlight_userinfo_form_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "</div><!-- �I�� hoge --></div><!-- �I�� d1 -->\n</div><!-- �I�� main -->\n<!-- �e���X�I�� -->\n";

# Google AdSense
	&googleadsense;

	if ($res > 0) {
		print "\n<div class=\"main\">\n";
	}

	# �q���X���[�v
	foreach (@log[1..$#log]) {
		($no, undef, $nam, $eml, $com, $dat, $ho, $pw, $url, $mvw, $myid, $tim, $upl{1}, $upl{2}, $upl{3}, $idcrypt, $log_user_id, $is_sage,
			$log_cookie_a, $log_history_id, $log_useragent, $log_is_private_browsing_mode, $log_first_access_datetime,
			$upl{4}, $upl{5}, $upl{6}) = @{$_};

		# NG�l�[���K�p���X���O���J�b�g�\���@�\
		($nam, $cut_nam) = &cut_name($nam);

		# sage�\��
		my $sage;
		if ($is_sage eq '1') {
			$sage = ' [sage] ';
		}

		$com = &auto_link($com, $in{'no'});
#�e���X�ȍ~
		print "\n\n<!-- ���X�X�^�[�g -->\n<div id=\"d$no\"><dl class=\"hoge\"><dt>";


	# �����e�{�^��
		if ($job ne "past") {
			print "<span class=\"mente\"></span>\n";
		}

		print "<span class=\"num\"><a id=\"$no\"></a><a name=\"$no\"></a><a onclick=\"dofocus()\" href=\"javascript:MyFace('>>$no\\n')\" title=\">>$no\">$no&nbsp;�F</a>&nbsp;</span>";
		print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam$cut_nam$sage</span>";
		print " <span class=\"ng_hide\">$dat";

# ID��\��
	if($idkey && $idcrypt) {
		print " <span class=\"res_poster_id\">ID: $idcrypt";
		# ID�����e���J�E���g�@�\ ���e�����o��
		my $resCount = @{$resCountPerPoster{$idcrypt}};
		if ($resCount > 4) {
			# Binary Search
			my ($low, $high) = (0, $resCount);
			while($low < $high) {
				my $cursor = int(($high-$low)/2 + $low);
				if($resCountPerPoster{$idcrypt}->[$cursor] < $no) {
					$low = $cursor + 1;
				} else {
					$high = $cursor;
				}
			}
			my $i = $resCountPerPoster{$idcrypt}->[$low] == $no ? ($low+1) : -1;
			print " <span class=\"hatugen_red\">[$i/$resCount]</span>";
		} elsif ($resCount > 1) {
			# Binary Search
			my ($low, $high) = (0, $resCount);
			while($low < $high) {
				my $cursor = int(($high-$low)/2 + $low);
				if($resCountPerPoster{$idcrypt}->[$cursor] < $no) {
					$low = $cursor + 1;
				} else {
					$high = $cursor;
				}
			}
			my $i = $resCountPerPoster{$idcrypt}->[$low] == $no ? ($low+1) : -1;
			print " <span class=\"hatugen_blue\">[$i/$resCount]</span>";
		}
		print "</span></span>";
	} else {
		print "</span>"
	}

	# �o�^ID���o��
	if ($webprotect_auth_res && $log_user_id ne '') {
		# ���[�U�����\���@�\
		if (exists($highlight_userinfo_colorindex_hash{user_id}->{$log_user_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{user_id}->{$log_user_id}]}[1];
			print " �o�^ID:<span class=\"user_id\"><span style=\"background-color:$color_code\">$log_user_id</span></span>";
		} else {
			print " �o�^ID:<span class=\"user_id\">$log_user_id</span>";
		}
	}

	# ����ID���o��
	if ($log_history_id ne '') {
		# ���[�U�����\���@�\
		# (����ID�ɖ�����@���܂܂�Ă���ꍇ�͏����Ă��猟������)
		(my $find_history_id = $log_history_id) =~ s/\@$//;
		if (exists($highlight_userinfo_colorindex_hash{history_id}->{$find_history_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{history_id}->{$find_history_id}]}[1];
			print " ����ID:<span style=\"background-color:$color_code\">$log_history_id</span>";
		} else {
			print " ����ID:$log_history_id";
		}
	}

	# ���j�[�NCookieA���o��
	if ($log_cookie_a ne '') {
		# ���[�U�����\���@�\
		if (exists($highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a}]}[1];
			print " CookieA:<span style=\"background-color:$color_code\">$log_cookie_a</span>";
		} else {
			print " CookieA:$log_cookie_a";
		}
	}

	# �z�X�g���o��
	## ���[�U�����\���@�\
	if (exists($highlight_userinfo_colorindex_hash{host}->{$ho})) {
		my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{host}->{$ho}]}[1];
		print " �z�X�g:<span style=\"background-color:$color_code\">$ho</span>";
	} else {
		print " �z�X�g:$ho";
	}

	# UserAgent���o��
	if ($log_useragent ne '') {
		# UserAgent�̋����\���@�\
		my $color_code;
		foreach my $setting_hashref (@highlight_ua_setting_hashref_array) {
			if (!$setting_hashref->{valid_flag}) {
				# ���Ԃ��o�߂��Ė����̐ݒ���X�L�b�v
				next;
			}
			my $target_host = $setting_hashref->{host};
			my $target_useragent = $setting_hashref->{useragent};
			my $color_index = $setting_hashref->{color};

			# ��v����
			if (defined(${$mu->get_matched_host_useragent_and_whether_its_not_match($ho, $log_useragent, "$target_host<>$target_useragent", undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)}[0])) {
				$color_code = ${$highlight_userinfo_color_name_code[$color_index]}[1];
				last; # �z��̐擪���猟�����A�ŏ��Ɉ�v�����ݒ�̐F���g�p����
			}
		}

		if (defined($color_code)) {
			print " UA:<span style=\"background-color:$color_code\">$log_useragent</span>";
		} else {
			print " UA:$log_useragent";
		}
	}

	# �v���C�x�[�g���[�h���L���ł���Ώo��
	if ($log_is_private_browsing_mode) {
		print ' �v���C�x�[�g���[�h:�L��';
	}

	# ����A�N�Z�X���Ԃ��L�^����Ă���ꍇ�͏o��
	if ($log_first_access_datetime ne '') {
		print " ����A�N�Z�X����:$log_first_access_datetime";
	}

	# �摜��MD5���o��
	foreach my $i (1 .. 6) {
		my ($image_orig_md5, $image_conv_md5) = (split(/,/, $upl{$i}))[6, 7];
		next if ($image_orig_md5 eq '');

		# �ϊ��OMD5���o��
		print " �摜$i:$image_orig_md5";

		# �ϊ���MD5���L�^����Ă���ꍇ�͑����ďo��
		if ($image_conv_md5 ne '') {
			print ",$image_conv_md5";
		}
	}

	# �uNG�l�[���o�^�v��\��(�uNG�l�[�������v�\����Javascript�ɂ���ăy�[�W���[�h��ɓ��I�ɍs����)
	if($ngname) {
		print " <a href=\"#\" class=\"ngname_toggle ng_toggle\">NG�l�[���o�^</a>";
	}

	# �uNGID�o�^�v��\��(�uNGID�����v�\����Javascript�ɂ���ăy�[�W���[�h��ɓ��I�ɍs����)
	if($idkey && $idcrypt && $ngid) {
		print " <a href=\"#\" class=\"ngid_toggle ng_toggle\">NGID�o�^</a>";
	}

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}




		print "";
		if ($eml && $mvw ne '0' && $show_mail==1) {
			print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;";
		}

# ID��\��
	if($idkey && $idcrypt) { print ""; }

			print "</dl></dt>\n";

# ���[�����M�t�H�[���ւ̃����NStart
	print <<"EOM";
EOM

#���O��ϊ�
#	�}�b�`����������̑O����擾($`, $')
#	http://www.perlplus.jp/regular/ref/index2.html

if ($nam =~ /��.*/){
#  print "<br>�O�̕��� : $`\n<br>";
#�}�b�`�������������
  $nam = $`;
#  print "�}�b�`���������� : $&\n<br>";
#  print "��̕��� : $'\n<br>";
}

		if ($url) {
			print "<dt>�Q�ƁF <a href=\"$url\" target=\"_blank\" rel=\"nofollow\">$url</a>\n";
		}
		print "\n<div class=\"comment\">$com</div>\n";

		my ($dd_flg, @img_filename);
		foreach $i (1 .. 6) {
			my ($img_folder_number, $ex, $w, $h, $thumb_w, $thumb_h) = split(/,/, $upl{$i});
			next if (!$ex);

			if (!$dd_flg) {
				print "<div class=\"comment-img\">";
				$dd_flg++;
			}

			if ($in{'noimage'}) {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			} elsif (defined($imgex{$ex})) {
#			if (defined($imgex{$ex})) {
				my $thumb_path, $width, $height;
				if($thumbnail && -f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
					# �T���l�C���摜�@�\���L�����T���l�C���摜�t�@�C�������݂��鎞
					($width, $height) = &resize($thumb_w, $thumb_h);
					$thumb_path = "$thumburl/$img_folder_number/$tim-${i}_s.jpg";
				} else {
					# �I���W�i���摜���k�����ăT���l�C���摜�\������ꍇ
					($width, $height) = &resize($w, $h);
					$thumb_path = "$uplurl/$img_folder_number/$tim-$i$ex";
				}
				# �T���l�C���摜��\���ł��鎞
				if($thumb_path && $width > 0 && $height > 0) {
					# �T���l�C���摜����уI���W�i���摜�ւ̃����N HTML�o��
					print "<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\"><img src=\"$thumb_path\" align=\"top\" border=\"0\" width=\"$width\" height=\"$height\" hspace=\"3\" vspace=\"5\"></a>\n";
					# �I���W�i���摜�t�@�C�����擾
					push(@img_filename, "�� $img_filename_prefix$img_folder_number/$tim-$i$ex ��");
				}
			} else {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			}
		}
		# �摜�t�@�C�����\��
		if (scalar(@img_filename) > 0) { print "<br><br>\n"; }
		print join("<br>\n", @img_filename) . "\n";
		if ($dd_flg) { print "</div>\n"; }

		# �X���b�h��ʂ��烆�[�U�𐧌�����@�\
		print "<div>\n" . create_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
		print "<div>\n" . create_restrict_user_by_time_range_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# �X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
		print "<div>\n" . create_in_thread_only_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

        # ���[�U�����\���@�\
        print "<br><div>\n" . create_highlight_userinfo_form_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "</div>\n<!-- ���X�I��-->\n";


	}

	print "<tr><td><br></td></tr>" if (!$i);
# ���[�����M�t�H�[���ւ̃����NEnd



	print <<"EOM";
<!-- google_ad_section_end -->
<!-- �I�� main -->
EOM
	# �y�[�W�J�z�{�^��
	if ($key != 2 && scalar(@log) > 1) {
		print pagelink($thread_no, $page_cnt, $all_flg);
	}

	# ���s���O/�ߋ����O �y�[�W���� ���ʕ\�����ڒ�`
	my $common_display_contents_at_bottom_of_page = '';
	{
		# �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\ �����N�\����
		$common_display_contents_at_bottom_of_page .= "<br><br>\n";
		for (my $i = 1; $i <= 6; $i++) {
			$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC
		}
		$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC


		## �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\ �����N�\����
		$common_display_contents_at_bottom_of_page .= "<br><br>\n";
		for (my $i = 1; $i <= 20; $i++) {
			$common_display_contents_at_bottom_of_page .= "<div>\n";
			for (my $j = 1; $j <= 6; $j++) {
				$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC
			}
			$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC
		}


		## ���[�U�����@�\ (CookieA�Ȃǂ��t�H�[������o�^) �t�H�[���\����
		$common_display_contents_at_bottom_of_page .= "<br><br>\n";
		# CSV�ꊇ���̓t�H�[��
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
<br>
EOC
		# ���ڕʓ��̓t�H�[��
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC


		## ���[�U�����\���@�\ (CookieA�Ȃǂ��t�H�[������o�^) �t�H�[���\����
		$common_display_contents_at_bottom_of_page .= "<br><br><br>\n";
		# CSV�ꊇ���̓t�H�[��
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</select>
</div>
<br>
EOC
		# ���ڕʓ��̓t�H�[��
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC


		## UserAgent�̋����\���@�\ (�z�X�g��UserAgent���t�H�[������o�^) �t�H�[���\����
		# �o�^�t�H�[��
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC
		# ���ݐݒ�v���_�E�����X�g �X�V/�폜�t�H�[��
		# (�ݒ肪1�ȏ゠��ꍇ�̂ݕ\��)
		if (scalar(@highlight_ua_setting_hashref_array) > 0) {
			$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
<select id="highlight_ua_form_current_settings">
EOC
			foreach my $setting_hashref (@highlight_ua_setting_hashref_array) {
				my $target_host_html = HTML::Entities::encode(${$setting_hashref}{host});
				my $target_useragent_html = HTML::Entities::encode(${$setting_hashref}{useragent});
				$common_display_contents_at_bottom_of_page .=
					"<option data-host=\"$target_host_html\" data-useragent=\"$target_useragent_html\">$target_host_html&lt;&gt;$target_useragent_html</option>\n";
			}
			$common_display_contents_at_bottom_of_page .= <<"EOC";
</select>
&nbsp;&nbsp;
<button type="button" id="highlight_ua_form_current_settings_update_timestamp">�X�V</button>
<span class="highlight_ua_form_current_settings_ajax_messages" id="highlight_ua_form_current_settings_update_timestamp_ajax_message"></span>
&nbsp;
<button type="button" id="highlight_ua_form_current_settings_remove">�폜</button>
<span class="highlight_ua_form_current_settings_ajax_messages" id="highlight_ua_form_current_settings_remove_ajax_message"></span>
</div>
EOC
		}


		## �\�����e����@�\ �y�[�W�����\������
		if ($is_branching_contents) {
			# �\���͈͂̃��X�ɐݒ肵�������񂪊܂܂�Ă��邩�A
			# �摜�`�F�b�N�L�����́A�摜���A�b�v����Ă���ꍇ
			$common_display_contents_at_bottom_of_page .= "<h2>�\\��2_YES</h2>\n";
		} else {
			# ����ȊO�̏ꍇ
			$common_display_contents_at_bottom_of_page .= "<h2>�\\��2_NO</h2>\n";
		}
	}

	if ($job ne "past" && ($key == 1 || $key == 3) && $ReadOnly == 0) {
		# ���s���O�ŃX���b�h���b�N����Ă��Ȃ����A���X�t�H�[���\��
		&form2('', $thread_title, \%first_res, $common_display_contents_at_bottom_of_page);
	} else {
		# �ߋ����O���X���b�h���b�N����Ă���ȂǁA���X�������݂ł��Ȃ���

		# �y�[�W���� ���ʕ\�����ڂ��o��
		print $common_display_contents_at_bottom_of_page;
	}
	print <<"EOM";

</div><!--�I�� wrapper-main-in-->
</div><!--�I�� wrapper-main-->


</div><!-- �I�� container -->




EOM



	print <<"EOM";



</ul>
</div><!-- �I�� header_s -->





</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �ʋL���{��
#-------------------------------------------------
sub view2 {
	# �X�}�C���A�C�R����`
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
	}

	# �����`�F�b�N
	$in{'f'}  =~ s/\D//g;

	# �L��No�F��
	if ($in{'no'} =~ /^\d+$/) { $ptn = 1; $start = $in{'no'}; }
	elsif ($in{'no'} =~ /^(\d+)\-$/) { $ptn = 2; $start = $1; }
	elsif ($in{'no'} =~ /^(\d+)\-(\d+)$/) { $ptn = 3; $start = $1; $end = $2; }
	else { &error("�L��No���s���ł�"); }

	# �X���b�h���O�t�@�C���p�X�擾
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";

	unless (-e $logfile_path) {
		 &error("�X������������܂���");
	}

	# �����̓��e��ڗ�������@�\ �L����Ԏ擾
	my $highlight_name_in_own_post = get_highlight_name_on_own_post();

	&header($sub);

	print <<"EOM";
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />


<script type="text/javascript"><!--
\$\(document).ready( function() {
    \$\(".scroll").scrollAnchors();
    prettyPrint();
});
// --></script>

<script src="./jquery.anchors.js" type="text/javascript"></script>
</head>
<body>
<script type="text/javascript">
function dofocus() {
    var element = document.getElementById("fokasuidou");
    element.focus(); // �J�[�\�������킹��
}
</script>


<div id="container">


<div id="wrapper-main">
<div id="wrapper-main-in">



EOM


#�X�������擾
#	local($flag, $top);
	local $top;
	open(IN, $logfile_path);
	$top = <IN>;
	local($no3,$sub,$res,$key) = split(/<>/, $top);
	$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

print <<"EOM";
<h1 id="kobetu">$sub</h1>
EOM



print <<"EOM";

EOM



#	local($flag, $top);
#	open(IN, $logfile_path);
#	$top = <IN>;
	local $flag;
	while (<IN>) {
		local ($no,$sub,$nam,$eml,$com,$dat,$ho,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$idcrypt,$user_id,$is_sage,$log_cookie_a,$log_history_id) = split(/<>/);
		if ($start == $no) { $flag=1; }
		if (!$flag) { next; }

		if (time < $tim + $hot) { $resicon = 'filenew.gif'; }
		else {$resicon = 'file.gif'; }

		# �L���\��

		if ($eml && $mvw ne '0' && $show_mail==1) {
			print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
		}


print "\n\n<!-- ���X�X�^�[�g -->\n<dl class=\"hoge\"><dt>";




	# �����e�{�^��
	if ($job ne "past") {
		print "<span class=\"mente\"></span><span class=\"num\">$no </span> \n";
	}

	print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam</span>  $dat";

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}



# ID��\��
	if($idkey && $idcrypt) { print ""; }
			print "</dt></dl>\n";

#�e���X�̖��O��




		$com = &auto_link($com, $in{'f'});

		print "<div class=\"comment\">$com</div>\n";

		if (($ptn == 3 && $end == $no) || ($flag && $ptn == 1)) { last; }
	}
	close(IN);

	if (!$flag) {
		print "<h3>�L������������܂���</h3>\n";
	}

	print <<"EOM";


</div><!--�I�� wrapper-main-in-->
</div><!--�I�� wrapper-main-->



</div><!-- �I�� container -->


</body>
</html>
EOM
	exit;
}


#-------------------------------------------------
#  �V�K�t�H�[��
#-------------------------------------------------
sub form {

	if ($ReadOnly) {
		&error("$Oshirase");
	}

	# �����`�F�b�N
	if ($authkey && $my_rank < 2) {
		&error("���e�̌���������܂���");
	}

	# �w�b�_
	if ($smile) { &header("", "js"); }
	else { &header(); }

	print <<"EOM";
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<div align="center">
<table width="95%">
<tr>
  <td align="right" nowrapper-main>
	<a href="$bbscgi?">�g�b�v�y�[�W</a> &gt; �V�K�X���b�h�쐬
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>�V�K�X���b�h�쐬�t�H�[��</b></td>
</tr></table></Td></Tr></Table>
EOM

	&form2("new");

	print "</div></body></html>\n";
	exit;
}

#-------------------------------------------------
#  �t�H�[�����e
#-------------------------------------------------

#-------------------------------------------------
sub form2 {
	# �ԐM���e��(�v���r���[�܂�)�́A$thread_title�A%first_res�̃n�b�V�����t�@�����X�A�y�[�W�����\��HTML(�X���b�h�\�����̂�)�������ɓn��
	my ($job, $thread_title, $first_res_hash_ref, $common_display_contents_at_bottom_of_page) = @_;

	# �t�H�[���\�����s�����ǂ����̃t���O������(�f�t�H���g�ł͕\��)
    my $display_form = 1;

	# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\�Ŏg�p����1���X���n�b�V��(�ԐM���e�E�v���r���[���̂ݎg�p)
	# �n�b�V�����t�@�����X���f���t�@�����X
	my %first_res;
	if (defined($first_res_hash_ref)) {
		%first_res = %{$first_res_hash_ref};
	}

	# �����`�F�b�N
	if ($authkey && $my_rank < 2) {
		return;
	}

	# �N�b�L�[�擾
	local($cnam,$ceml,$cpwd,$curl,$cmvw,undef,$cuser_pwd,$cthread_sort,$cthread_sage,$csave_history,$cincrease_upload_num_checked) = &get_cookie;
	if ($in_url==0 || $in_url==1){
	if ($curl eq "") { $curl = "http://"; }
	}

	# �v���r���[�p�ɃN�b�L�[�����㏑��
	if ($job eq "preview" || $job eq "resview" ) {
		$cnam=$i_nam;
		$ceml=$in{'email'};
		$cpwd=$in{'pwd'};
		if(($job eq "preview" ? $webprotect_auth_new : $webprotect_auth_res)) {
			$cuser_id=$in{'user_id'};
			$cuser_pwd=$in{'user_pwd'};
		}
		if ($in_url==0 || $in_url==1){
		$curl=$in{'url'};
		}
		$cmvw=$in{'mvw'};
	} else {
	# �v���r���[����Ȃ��Ƃ��͕ҏW�s�\�I�v�V�����𖳌���
		$editpreview='';
	}
#		$editpreview='';

	# ���񏑂����݂܂ł̎��Ԑ����@�\
	if ((my $left_hours = $first_cookie->get_left_hours_of_restriction()) > 0) {
		$display_form = 0;
		my $restrict_hours = $first_cookie->get_hours_of_restriction();
		if ($job eq 'new' || $job eq 'preview') {
			print <<"EOM";
<h3 style=\"color: #ff0000;\">�X���b�h�쐬���\\�ɂȂ�܂ł���${left_hours}���Ԃł��B��${restrict_hours}</h3>
EOM
		} else {
			print "<h3 style=\"color: #ff0000;\">���X���\\�ɂȂ�܂ł���${left_hours}���Ԃł��B��${restrict_hours}</h3>\n";
		}
	}

	# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �C���X�^���X������
	my $thread_create_post_restrict = ThreadCreatePostRestrict->new(
		$mu,
		$thread_create_post_restrict_settings_filepath,
		$host, $useragent, $cookie_a, $cuser_id, $chistory_id, 0,
		$cookie_a_instance
	);

	# �X���b�h�쐬�����@�\
	if ($job eq 'new' || $job eq 'preview') {
		# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �X���b�h�쐬�����@�\ ������Ԏ擾
		my $thread_create_restrict_status = $thread_create_post_restrict->determine_thread_create_restrict_status();

		my $err_msg_html;
		if ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a, $cuser_id, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a, $cuser_id, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
		) {
			$display_form = 0;
			$err_msg_html = "���̃z�X�g����X���b�h�쐬�͂ł��܂���B";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_2) {
			$display_form = 0;
			$err_msg_html = "���̃z�X�g����X���b�h�쐬�͂ł��܂���B(�����N���hogehoge�ł̓X���b�h�쐬���ł��܂��B)";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_3) {
			$display_form = 0;
			$err_msg_html = "�X���b�h�̍쐬�͏o���܂���B����";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_4) {
			$display_form = 0;
			$err_msg_html = "�X���b�h�̍쐬�͏o���܂���B����";
		} elsif (!$webprotect_auth_new
			&& $thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_5) {
			# �����I��WebProtect�ɂ��o�^ID�F�؂��s�킹��
			$webprotect_auth_new = 1;
		}
		# �G���[���b�Z�[�W������ꍇ�͕\������
		if ($err_msg_html) {
			print <<"EOM"
<h3 style=\"color: #ff0000;\">$err_msg_html</h3>
EOM
		}
	}

	# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\(���X�t�H�[���\�����̂�)
	if ($display_form && ($job eq '' || $job eq 'resview')) {
		# �O���t�@�C���ɂ��X���b�h�쐬�����@�\�Ȃǂ̓��� �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\ ������Ԏ擾
		my $post_restrict_status = $thread_create_post_restrict->determine_post_restrict_status_by_thread_title(
			$thread_title, $first_res{'host'}, $first_res{'url'}, $first_res{'user_id'}, $first_res{'cookie_a'}, $first_res{'history_id'}
		);

		my $msg;
		if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a, $cuser_id, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a, $cuser_id, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
			|| $mu->is_in_thread_only_restricted_user_from_thread_page($in{'no'}, $cookie_a, $cuser_id, $chistory_id, $host) # �X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
		) {
			$msg = "<h3 style=\"color: #ff0000;\">���̃z�X�g����A���̃X���b�h�ւ̏������݂͏o���܂���B</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2) {
			$msg = "<h3 style=\"color: #ff0000;\">���̃z�X�g����A���̃X���b�h�ւ̏������݂͏o���܂���B<br>�����N���hogehoge�ł͏������߂܂��B</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3) {
			$msg = "<h3 style=\"color: #ff0000;\">���̃X���b�h�ւ̏������݂͏o���܂���B����</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4) {
			$msg = "<h3 style=\"color: #ff0000;\">���̃X���b�h�ւ̏������݂͏o���܂���B����</h3>\n";
		} elsif (!$webprotect_auth_res
			&& $post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5) {
			# �����I��WebProtect�ɂ��o�^ID�F�؂��s�킹��
			# (�������݃t�H�[����\����x�����\���͍s��Ȃ�)
			$webprotect_auth_res = 1;
			$msg = '';
		}
		if (defined($msg)) {
			if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION) {
				# �X���b�h�쐬�҂̏��O�@�\
				# �X���b�h�쐬�҂Ɣ��肳��A>>1��URL����jogai�Ǝw�肳��Ă���Ƃ�
				print "<h3 style=\"color: #ff0000;\">�X���b�h�쐬�҂̏ꍇ�͏������݂��o���܂��B</h3>\n";
			} elsif ($msg ne '') {
				# �X���b�h�쐬�҈ȊO���A>>1��URL����jogai�Ǝw�肳��Ă��Ȃ��ꍇ�́A
				# �������݃t�H�[����\���ƌx�����\�����s��
				$display_form = 0;
				print $msg;
			}
		}
	}

	# �������݂ł���z�X�g�ł̂݁A�t�H�[����\��
	if ($display_form) {
        # �z�X�g�Ȃǂɂ��摜�A�b�v���[�h�̖���
        my $show_image_upl_buttons = $image_upl;
		$show_image_upl_buttons &&= !$mu->is_disable_upload_img($thread_title, $host, $useragent, $cookie_a, $cuser_id, $chistory_id, 0, \@disable_img_upload);

        # �z�X�g�Ȃǂɂ��age�̖���
        my $show_sage_checkbox = !defined($thread_title) || !$mu->is_disable_age($thread_title, $host, $useragent, $cookie_a, $cuser_id, $chistory_id, 0, \@disable_age);

		my $submit;
		if ($job eq "new" && $restitle) {
			print qq|<form action="$registcgi" method="post" name="myFORM"|;
		} elsif ($restitle) {
			print qq|<form action="$registcgi" method="post" name="myFORM"|;
		} elsif ($job eq "new") {
			print qq|<form action="$readcgi" method="post" name="myFORM"|;
		} elsif ($job eq "preview") {
			print qq|<form action="$registcgi" method="post" name="myFORM"|;
		} elsif ($job eq "resview") {
			print qq|<form action="$registcgi" method="post" name="myFORM"|;
		} else {
			print qq|<form action="$readcgi" method="post" name="myFORM"|;
		}
		if (($job eq "preview" || $job eq "resview" || $restitle) && $show_image_upl_buttons) {
			print qq| enctype="multipart/form-data"|;
		}
		print qq| id="postform">\n|;

		if ($restitle) {
			print <<EOM;
<input type="hidden" name="mode" value="regist">
<input type="hidden" name="pm">
EOM
		} elsif ($job eq "new") {
			print <<EOM;
<input type="hidden" name="mode" value="preview">
EOM
		} elsif ($job eq "preview") {
			print <<EOM;
<input type="hidden" name="mode" value="regist">
EOM
		} elsif ($job eq "resview") {
			print <<EOM;
<input type="hidden" name="mode" value="regist">
EOM
		} else  {
			print <<EOM;
<input type="hidden" name="mode" value="resview">
EOM
		}

		# <input type="hidden" name="mode" value="regist">

		print <<EOM;
EOM

		# <input type="text" name="sub" size="10" value="$resub" maxlength="10">

		if ($job eq "preview") {
			print <<EOM;
�薼
<input type="text" name="sub" size="10" value="" maxlength="10"> <font color="$col4">���e��\\���薼�����Ă�������</font>
EOM
			$submit = '�X���b�h�𐶐�';
		} elsif ($job eq "resview") {
			print <<EOM;
  �薼
<input type="text" name="sub" size="10" value="t" maxlength="10"> <font color="$col4">���e��\\���薼�����Ă�������</font>
EOM
			$submit = '�ԐM����';
			print "<input type=\"hidden\" name=\"res\" value=\"$in{'res'}\">\n";
			print "<input type=\"hidden\" name=\"l\" value=\"$in{'l'}\">\n";
            if ($show_sage_checkbox) {
                print "<input type=\"checkbox\" name=\"sage\" value=\"1\"";
                if ($cthread_sage eq '1') { print " checked"; }
                print ">sage\n";
            } else {
                print "<input type=\"hidden\" name=\"sage\" value=\"1\">\n";
            }
		} elsif ($job eq "new") {
			if ($restitle) {
				print <<EOM;
  �薼
<input type=\"input\" name=\"sub\" size=\"10\" value=\"\" maxlength=\"10\">

<br><br>
�J�e�S���F<br>
<input type="radio" name="add_sub" value="" checked>�f�t�H���g<br>
<input type="radio" name="add_sub" value="_cate1">�J�e�S��1<br>
<input type="radio" name="add_sub" value="_cate2">�J�e�S��2
EOM
				$submit = '�X���b�h�𐶐�';
			} else {
				print <<EOM;
  �薼
�^�C�g���͎��̉�ʂŐݒ肵�Ă�������
EOM
				$submit = '�v���r���[';
			}
		} else {
			# ���X�̏ꍇ�̏���
			# 		print <<EOM;
			#   �薼
			# <input type="text" name="sub" size="10" value="$resub" maxlength="10">
			# EOM
			print <<EOM;
  �薼
EOM
			if ($restitle) {
				print "<input type=\"input\" name=\"sub\" size=\"3\" value=\"t\" maxlength=\"3\">\n";
				$submit = ' �ԐM���� ';
                if ($show_sage_checkbox) {
                    print "<input type=\"checkbox\" name=\"sage\" value=\"1\"";
                    if ($cthread_sage eq '1') { print " checked"; }
                    print ">sage\n";
                } else {
                    print "<input type=\"hidden\" name=\"sage\" value=\"1\">\n";
                }
			} else {
				print "�^�C�g���͎��̉�ʂŐݒ肵�Ă�������\n";
				$submit = ' �ԐM�̃v���r���[ ';
			}
			print "<input type=\"hidden\" name=\"res\" value=\"$in{'no'}\">\n";
			print "<input type=\"hidden\" name=\"l\" value=\"$in{'l'}\">\n";
		}

		print <<"EOM";
<br>���O
EOM
		# ���O����\���@�\ (���X�t�H�[���\�����̂�)
		if (($job ne '' && $job ne 'resview') || !$mu->is_hide_name_field_in_form($thread_title, \@hide_form_name_field)) {
			print "    <input type=\"text\" name=\"name\" size=\"10\" value=\"$cnam\" maxlength=\"20\"><br>�u���O#�C�ӂ̕�����v�Ńg���b�v����\n";
		}
		print <<"EOM";
EOM

		if ($in_mail == 2) {
		} else {

			print <<"EOM";
EOM
			if ($in_mail != 1) {
				print "  <input type=\"text\" name=\"email\" size=\"30\" value=\"$ceml\">";
				if ($show_mail) {
					print "  <select name=\"mvw\">\n";
					if ($cmvw eq "") { $cmvw = 0; }
					@mvw = ('��\��','�\��');
					foreach (0,1) {
						if ($cmvw == $_) {
							print "<option value=\"$_\" selected>$mvw[$_]\n";
						} else {
							print "<option value=\"$_\">$mvw[$_]\n";
						}
					}
					print "</select>\n";
				} elsif ($usermail) {
					print "  <input type=\"hidden\" name=\"mvw\" value=\"0\"> ���͂���� <img src=\"$imgurl/mail.gif\" alt=\"���[���𑗐M����\" width=\"16\" height=\"13\" border=\"0\"> ���烁�[�����󂯎��܂��i�A�h���X��\\���j\n";
					if ($mailnotify==1 && $job eq "new") {
						print "�X���b�h�쐬�҂ɂ̓��X�������ꍇ�A���[���ł��m�点���܂�\n";
					} elsif ($mailnotify==2) {
						print "�܂��A�������݂������X���b�h�Ƀ��X�������ꍇ�A���[���ł��m�点���܂�\n";
					}
				} else {
				}
				if ($in_mail == 3) {
					print " ���f���e�h�~�̂��߉��������Ɠ��e�ł��܂���\n";

				} elsif ($in_mail == 1) {
					print " �i�K�{�j\n";
				}
			}
			print <<EOM;
EOM
		}

		if ($in_url==2) {

			print <<EOM;
EOM

		} else {

			print <<EOM;
URL
EOM

			if ($in_url==1){
				print " �K���������͂��Ȃ��Ɠ��e�ł��܂���\n";
			}
			if ($in_url==3){
				print " ���f���e�h�~�̂��߉��������Ɠ��e�ł��܂���\n";
			}

			print <<EOM;
EOM

		}

		# �摜�t�H�[��
		if ($image_upl && ($job eq "preview" || $job eq "resview" || $restitle && ($job eq 'new' || $job eq ""))) {
			print "<b>�摜�Y�t</b><br><span style=\"font-size:9px\">";
			print join('/', map { $_ =~ s/^\.//; uc($_); } sort(grep { $imgex{$_}; } keys(%imgex)));
			if ($show_image_upl_buttons) {
				if ($upl_increase_num > 0) {
					print "<input type=\"hidden\" name=\"increase_num\" value=\"0\">\n";
					print '<input type="checkbox" name="increase_num" id="increase_upload_num_checkbox" value="1"';
					if ($cincrease_upload_num_checked) {
						print ' checked';
					}
					print "> 4���ȏ�<br>\n";
				}
				foreach my $i (1 .. 3) {
					print "<input type=\"file\" name=\"upfile$i\" size=\"45\"><br>\n";
				}
				if ($upl_increase_num > 0) {
					print '<div id="up_add_field"';
					if (!$cincrease_upload_num_checked) {
						print ' style="display: none;"';
					}
					print ">\n";

					my $max_num = 3 + $upl_increase_num;
					foreach my $i (4 .. $max_num) {
						print "<input type=\"file\" name=\"upfile$i\" size=\"45\" class=\"up_add_files\"";
						if (!$cincrease_upload_num_checked) {
							print ' disabled';
						}
						print "><br>\n";
					}

					print "</div>\n";
				}
			}
		}

		elsif ($image_upl && !$restitle && ($job ne 'new' || $job ne "")) {
			print "<b>�摜�Y�t</b><br><span style=\"font-size:9px\">";
			print join('/', map { $_ =~ s/^\.//; uc($_); } sort(grep { $imgex{$_}; } keys(%imgex)));

		}
		# �͋Z�œW�J
		#			print "<input type=\"file\" name=\"upfile1\" value=\"$in{'upfile1'}\" size=\"45\"><br>\n";
		#			print "<input type=\"file\" name=\"upfile2\" value=\"$in{'upfile2'}\" size=\"45\"><br>\n";
		#			print "<input type=\"file\" name=\"upfile3\" value=\"$in{'upfile3'}\" size=\"45\"><br>\n";


		print <<EOM;
�p�X���[�h
  <input type="password" name="pwd" size="8" value="$cpwd" maxlength="8">
   �i�L�������e���Ɏg�p�j
EOM
		if(($webprotect_auth_new && ($job eq "new" || $job eq "preview")) || $webprotect_auth_res && ($job eq "" || $job eq "resview")) {
			print <<EOM;
�o�^ID
  <input type="text" name="user_id" size="30" value="$cuser_id">
�o�^�p�X���[�h
  <input type="password" name="user_pwd" size="30" value="$cuser_pwd">
EOM
        }

		# reCAPTCHA�F�ؕ\������
		my $is_recaptcha_enabled = 0;
		if ($recaptcha_thread && (($restitle && $job eq "new") || (!$restitle && $job eq "preview"))) {
			# �X���b�h�쐬��
			# �������O�I�[�v��
			my $create_log_fh;
			if (open($create_log_fh, '<', $recaptcha_thread_create_log) && flock($create_log_fh, 1)) {
				# �폜���O�s���J�E���g
				my $create_count = 0;
				while (sysread $create_log_fh, my $buffer, 4096) {
					$create_count += ($buffer =~ tr/\n//);
				}
				$create_count--; # �擪�s������������
				if ($create_count + 1 > $recaptcha_thread_permit) {
					# �X���b�h�A���쐬���e���𒴂��ď������݂��悤�Ƃ��Ă��邽�߁AreCAPTCHA�F�؂�L��
					$is_recaptcha_enabled = 1;
				}
				close($create_log_fh);
			}

			# reCAPTCHA�F�ؑΏۃz�X�g���O�I�[�v��
			# �z�X�g����v����ꍇ�͍X�V�A����ȊO�ł��F�ؑΏۂ̏ꍇ�͒ǋL����
			my $auth_host_log_fh;
			if (open($auth_host_log_fh, '+>>', $recaptcha_thread_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) {
				my $auth_host_log = "����,�X���b�h�^�C�g��,�z�X�g,�^�C���X�^���v\n";
				<$auth_host_log_fh>; # �擪�s�ǂݔ�΂�
				while (<$auth_host_log_fh>) {
					chomp($_);
					my $log_host = (split(/,/, $_))[2];
					if ($log_host eq $host) {
						$is_recaptcha_enabled = 1;
					} else {
						$auth_host_log .= "$_\n";
					}
				}
				if ($. < 1 || $is_recaptcha_enabled) {
					if ($is_recaptcha_enabled) {
						$auth_host_log .= "$date,$thread_title,$host,$time\n";
					}
					seek($auth_host_log_fh, 0, 0);
					truncate($auth_host_log_fh, 0);
					print $auth_host_log_fh $auth_host_log;
				}
				close($auth_host_log_fh);
			}
		} else {
			# ���X���̓��O�ɂ��\��������s�킸�A�ݒ�l�݂̂Ő؂�ւ���
			$is_recaptcha_enabled = $recaptcha_res && (($restitle && $job eq "") || (!$restitle && $job eq "resview"));
		}

		# ���e�L�[
		if ($is_recaptcha_enabled) {
			print <<"EOM"
���e�L�[
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <div class="g-recaptcha" data-sitekey="${recaptcha_site_key}"></div>
    <noscript>
      <div style="width: 302px; height: 422px;">
        <div style="width: 302px; height: 422px; position: relative;">
          <div style="width: 302px; height: 422px; position: absolute;">
            <iframe src="https://www.google.com/recaptcha/api/fallback?k=${recaptcha_site_key}"
                    frameborder="0" scrolling="no"
                    style="width: 302px; height:422px; border-style: none;">
            </iframe>
          </div>
          <div style="width: 300px; height: 60px; border-style: none;
                      bottom: 12px; left: 25px; margin: 0px; padding: 0px; right: 25px;
                      background: #f9f9f9; border: 1px solid #c1c1c1; border-radius: 3px;">
            <textarea id="g-recaptcha-response" name="g-recaptcha-response"
                      class="g-recaptcha-response"
                      style="width: 250px; height: 40px; border: 1px solid #c1c1c1;
                             margin: 10px 25px; padding: 0px; resize: none;" >
            </textarea>
          </div>
        </div>
      </div>
    </noscript>
EOM
		} elsif (($regist_key_new && $job eq "new") || ($regist_key_res && $job eq "")) {

			# �L�[����
			require $regkeypl;
			local($str_plain,$str_crypt) = &pcp_makekey;

			# ���̓t�H�[��
			print qq |���e�L�[|;
			print qq |<input type="text" name="regikey" size="6" style="ime-mode:inactive">\n|;
			print qq |�i���e�� <img src="$registkeycgi?$str_crypt" align="absmiddle" alt="���e�L�["> ����͂��Ă��������j\n|;
			print qq |<input type="hidden" name="str_crypt" value="$str_crypt">\n|;
			#	}
			#	if ($regist_key && $job eq "preview") {
		} elsif ($regist_key_new && $job eq "preview" || ($regist_key_res && $job eq "resview")) {

			if ($in{'regikey'} eq "") {
				require $regkeypl;
				local($str_plain,$str_crypt) = &pcp_makekey;
				$in{'str_crypt'}=$str_crypt;
			}

			print qq |���e�L�[|;
			print qq |<input type="text" name="regikey" size="6" value="$in{'regikey'}" style="ime-mode:inactive">\n|;
			print qq |�i���e�� <img src="$registkeycgi?$in{'str_crypt'}" align="absmiddle" alt="���e�L�["> ����͂��Ă��������j\n|;
			print qq |<input type="hidden" name="str_crypt" value="$in{'str_crypt'}">\n|;
		}

		print <<EOM;
�R�����g
EOM

		# �A�C�R��
		if ($smile) {
			@s1 = split(/\s+/, $smile1);
			@s2 = split(/\s+/, $smile2);
			foreach (0 .. $#s1) {
				print "<a href=\"javascript:MyFace('$s2[$_]')\">";
				print "<img src=\"$imgurl/$s1[$_]\" border=\"0\"></a>\n";
			}
			print "<br>\n";
		}

		if ($job eq "new") {
			print <<"EOM";
<font color="$col4">$createnotice</font><br>
EOM
			$rows=$newrows;
		}

		if ($editpreview) {
			print <<"EOM";
<textarea name="comment" cols="15" rows="15" wrap="soft" name="fokasuidou" id="fokasuidou" readonly style="color:#999999">
EOM
		} else {
			print <<"EOM";
<textarea name="comment" cols="15" rows="15" wrap="soft" name="fokasuidou" id="fokasuidou">
EOM
		}

		# �V�K�X���̓e���v���W�J
		if ($job eq "new") {
			print "$createtemplate\n";
		}
		# �v���r���[��
		if ($job eq "preview" || $job eq "resview" ) {
			print "$i_com";
		}

		print <<"EOM";
</textarea>
<br>
    <input type="submit" value="$submit"> &nbsp;&nbsp;
    <input type="checkbox" name="cook" value="on" checked>�N�b�L�[�ۑ� &nbsp;&nbsp;
EOM
		#�v���r���[�@�\�𖳌����i$restitle = 1;�j�A�X���b�h�쐬��ʂɁu�m�F�v�̃`�F�b�N�{�b�N�X��\�����܂��B
		if($restitle && $in{'mode'} eq 'form') {
			print<<"EOM";
			<input type="checkbox" name="confirm" value="on">�m�F
EOM
	}
	print<<"EOM";

  </form>
EOM

        # �������ݗ����ɋL�^�`�F�b�N�{�b�N�X(����ID���s�y�[�W�w�̃����N)
		if ($job eq "new") {
			print '';
		}
		if (defined($chistory_id)) {
			# �`�F�b�N�{�b�N�X�Ƀ`�F�b�N�����Ȃ��ꍇ�̑��M�l
			print "<input type=\"hidden\" name=\"save_history\" value=\"0\">\n";
		}
        print "<input type=\"checkbox\" name=\"save_history\" value=\"1\"";
        if (!defined($chistory_id)) {
            print ' disabled';
        } elsif ($csave_history == 1 || $csave_history eq '') {
			print ' checked';
		}
        print '> �L�^�i';
        if (defined($chistory_id)) {
            print "ID�F$chistory_id";
        } else {
            print "<a href=\"$history_webprotect_issue_url\">�y����ID���s�z</a>";
            print "<div style=\"text-align: right\"><a href=\"./admin.cgi?action=log&file=$in{'no'}\">���O�̉{��</a></div>";
        }
		if ($job eq "new") {
			print "�j\n";
		} else {
			print "�j<br>\n";
		}
	}

	if ($job ne "preview" && $job ne "new") {
		# �y�[�W���� ���ʕ\�����ڂ��o��
		print $common_display_contents_at_bottom_of_page;

		print <<"EOM";
EOM

		print "<br><br>\n";
		print <<"EOM";
EOM
		if (exists($in{'no'})) {
			print "<input type=\"hidden\" name=\"no\" value=\"$in{'no'}\">\n";
			if (exists($in{'p'})) {
				print "<input type=\"hidden\" name=\"p\" value=\"$in{'p'}\">\n";
			}
			if (exists($in{'l'})) {
				print "<input type=\"hidden\" name=\"l\" value=\"$in{'l'}\">\n";
			}
		}
		print <<"EOM";



</div>
EOM
	}
}

#-------------------------------------------------
#  �ߋ����O�{��
#-------------------------------------------------
sub past {
	# �L���{��
	if ($in{'no'}) { &view("past");	}

	&header();
	print <<"EOM";
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%"><tr><td align="right" nowrapper-main>
<a href="$bbscgi?">�g�b�v�y�[�W</a> &gt; �ߋ����O
</td></tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1" class="td0">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/memo1.gif" align="middle">
&nbsp;<b>�ߋ����O</b></td>
</tr></table></Td></Tr></Table>

<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="16"><br></td>
  <td bgcolor="$col2" width="80%"><b>�X��</b></td>
  <td bgcolor="$col2" nowrapper-main><b>���e��</b></td>
  <td bgcolor="$col2" nowrapper-main><b>�ԐM��</b></td>
  <td bgcolor="$col2" nowrapper-main><b>�ŏI�X�V</b></td>
</tr>
EOM

	# �X���W�J
	local($i) = 0;
	if ($p eq "") { $p = 0; }
	# �J�e�S���\���@�\�̗L����Ԃɂ���ď�������ύX���邽�߁A
	# ���O�ǂݎ�莞�̊e�������T�u���[�`��������
	my $countLog = sub {
		# �Ώۃ��O�Ƃ��Č����J�E���g���A�\���ΏۊO�̏ꍇ�X�L�b�v����
		$i++;
		next if ($i < $p + 1);
		last if ($i > $p + $menu2);
	};
	my $readLog = sub {
		# ���O��ǂݎ��A�e���ڂ�ϐ��ɑ�����ă��X�g�ŕԂ�
		chomp($_);
		($no,$sub,$res,$name,$date,$host) = (split(/<>/))[0..4,10];
		$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
	};
	my $judgeCategory = sub {
		next if $sub !~ /$in{'k'}$/; # �^�C�g�������ɃJ�e�S�������܂܂Ȃ��ꍇ�̓X�L�b�v����
	};
	open(IN,"$pastfile") || &error("Open Error: $pastfile");
	while (<IN>) {
		local ($no,$sub,$res,$name,$date,$host);

		# ���O�ǂݎ�菈�����s
		if ($in{'k'} eq '') {
			# �J�e�S���\���@�\ ������
			$countLog->();
			$readLog->();
		} else {
			# �J�e�S���\���@�\ �L����
			$readLog->();
			$judgeCategory->();
			$countLog->();
		}

		# �X���b�h�ꗗ���O�t�@�C���ɃX���b�h�쐬�҃z�X�g���̋L�^���Ȃ��ꍇ
		# �X���b�h���O�t�@�C�����ǂݍ��݁i���X���b�h�ꗗ���O�t�@�C���t�H�[�}�b�g�Ƃ̌݊����̂��߂̎���)
		if ($host eq '') {
			my $logfile_path = get_logfolder_path($no) . "/$no.cgi";
			open(THREAD, $logfile_path);
			<THREAD>;
			my $topRes = <THREAD>;
			if(defined($topRes)) {
				$host = (split(/<>/, $topRes))[6];
			}
			close(THREAD);
		}

		print "<tr bgcolor=\"$col2\"><td bgcolor=\"$col2\" width=\"16\">";
		print "<img src=\"$imgurl/fold1.gif\"></td>";
		print "<td bgcolor=\"$col2\" width=\"80%\">";
		print "<a href=\"$readcgi?no=$no&mode=past\">[$no] $sub</a> <span class=\"s1\">$host</span></td>";
		print "<td bgcolor=\"$col2\" nowrapper-main>$name</td>";
		print "<td bgcolor=\"$col2\" align=\"right\" nowrapper-main class=\"num\">$res</td>";
		print "<td bgcolor=\"$col2\" nowrapper-main class=\"s1\">$date</td></tr>\n";
	}
	# �c��̕\���͈͊O�̃X���b�h�����J�E���g
	if ($in{'k'} eq '') {
		# �J�e�S���\���@�\�������̓o�b�t�@�Ɉ�Ăɓǂݍ��݉��s���J�E���g
		local $/ = undef;
		my $buffer = <IN>;
		$i += ($buffer =~ tr/\n//);
	} else {
		# �L������1�s���^�C�g����������v���邩�m�F���ăJ�E���g
		while(<IN>) {
			chomp($_);
			(my $sub = (split(/<>/))[1]) =~ s/\0*//g;
			$i++ if $sub =~ /$in{'k'}$/;
		}
	}
	close(IN);

	if (!$i) {
		print "<td bgcolor=\"$col2\"></td>";
		print "<td colspan=\"4\" bgcolor=\"$col2\">- ���݉ߋ����O�͂���܂��� -</td>\n";
	}

	print "</table></Td></Tr></Table>\n";

    # �y�[�W�ړ��{�^���\��
    if ($p - $menu2 >= 0 || $p + $menu2 < $i) {
        print "<br><br><table>\n";

        # ���ݕ\���y�[�W/�S�y�[�W���\��
        my $pages = int(($i - 1) / $menu2) + 1; # �S�y�[�W���擾
        if ($p < 0) {
            # �}�C�i�X���w�肳�ꂽ���́A1�y�[�W�ڂƂ���
            $p = 0;
        } elsif ($p + 1 > $i) {
            # �S�X���b�h�������傫���l���w�肳�ꂽ���́A�ŏI�y�[�W�w��Ƃ���
            $p = ($pages - 1) * $menu2;
        }
        my $current_page = int($p / $menu2) + 1; # ���ݕ\���y�[�W�擾
        print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

        # 1�y�[�W�ځE�O��y�[�W�E�ŏI�y�[�W�ւ̃����N
        my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
        print "<tr><td class=\"num\">";
        if ($current_page <= 1) {
            print "&lt;&lt;�@�O�ց@";
        } else {
            my $prev_page = ($current_page - 2) * $menu2;
            print "<a href=\"$readcgi?mode=past&${k_html}p=0\">&lt;&lt;</a>�@<a href=\"$readcgi?mode=past&${k_html}p=$prev_page\">�O��</a>�@";
        }
        if ($current_page >= $pages) {
            print "���ց@&gt;&gt;";
        } else {
            my $next_page = $current_page * $menu2;
            my $last_page = ($pages - 1) * $menu2;
            print "<a href=\"$readcgi?mode=past&${k_html}p=$next_page\">����</a>�@<a href=\"$readcgi?mode=past&${k_html}p=$last_page\">&gt;&gt;</a>";
        }
        print "</td></tr>\n";

        print "</table>\n";
    }

	print <<"EOM";
</div><!--�I�� wrapper-main-in-->
</div><!--�I�� wrapper-main-->



EOM

	print "</div><!-- �I�� container -->\n</body></html>\n";
	exit;
}


#-------------------------------------------------
#  �y�[�W�J�z�{�^��
#-------------------------------------------------
sub pagelink {
	my ($thread_no, $page_cnt, $all_flg) = @_;

    # �e�[�u���u���b�N�n��
	my $pglog .= "<table>\n";

    # �S���X�\���t���O�������Ă��Ȃ����̂݁A�y�[�W�ړ������N��\��
    if (!$all_flg) {
        # ���ݕ\���y�[�W/�S�y�[�W���\��
        $pglog .= "<tr><td class=\"num\" align=\"center\">$p/$page_cnt</td></tr>\n";

        # 1�y�[�W�ځE�O��y�[�W�E�ŏI�y�[�W�ւ̃����N
        my $l_html = exists($in{l}) ? "&l=$in{l}" : "";
        $pglog .= "<tr><td class=\"num\" align=\"center\">";
        if ($p <= 1 || $all_flg) {
            $pglog .= "&lt;&lt;�@�O�ց@";
        } else {
            my $prev_page = $p - 1;
            $pglog .= "<a href=\"$readcgi?no=$thread_no&p=1$l_html\">&lt;&lt;</a>�@<a href=\"$readcgi?no=$thread_no&p=$prev_page$l_html\">�O��</a>�@";
        }
        if ($p >= $page_cnt || $all_flg) {
            $pglog .= "���ց@&gt;&gt;";
        } else {
            my $next_page = $p + 1;
            $pglog .= "<a href=\"$readcgi?no=$thread_no&p=$next_page$l_html\">����</a>�@<a href=\"$readcgi?no=$thread_no&p=$page_cnt$l_html\">&gt;&gt;</a>";
        }
		# 1�ڂ�td���^�O�̎��̋�td�^�O�́u�����܂œǂ񂾋@�\�v���쌋�ʕ\���Z���̓��e�ω��ɂ��
		# �y�[�W�ړ������N�̕\���ʒu��ω������Ȃ����߂̒����p�_�~�[�Z���ł�
        $pglog .= "</td><td></td></tr>\n";
    }

    # �󋵕\���E���̑������N
    $pglog .= "<tr><td class=\"num\">\n";
    if ($all_flg) {
        # �S���X�\���t���O�������Ă��鎞
        $pglog .= "�i�S���\\�����j <a href=\"$readcgi?no=$thread_no\">���ǂ�</a>\n";
    } else {
        $pglog .= "<a href=\"$readcgi?no=$thread_no&l=$no2-\">�S���\\��</a>\n";
    }
	$pglog .= "<a href=\"$bbscgi\">�X���b�h�ꗗ</a>\n";
	if (!$createonlyadmin) {
		$pglog .= "<a href=\"$readcgi?mode=form\">�V�K�X���b�h�쐬</a>\n";
	}

	# �����܂œǂ񂾋@�\ �����N
	$pglog .= "<a href=\"#\" class=\"readup_here\" data-threadno=\"$thread_no\">���C�ɓ���</a></td>\n";
	$pglog .= "<td class=\"num readup_here_op_result\"></td>\n";

	$pglog .= "</tr>\n";

    # �e�[�u���u���b�N�I���
    $pglog .= "</table>\n";

	return $pglog;
}

#-------------------------------------------------
#  �����N����
#-------------------------------------------------
sub auto_link {
	local($msg, $f) = @_;
	local($1, $2, $3, $4, $5); # �Ăяo��������̃}�b�`�ϐ����������

	$msg =~ s/([^=^\"]|^)(http[s]?\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
#	$msg =~ s/([^=^\"]|^)(https\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\">$2<\/a>/g;
# ���XNo�w��i�\���n�������j�j
#	$msg =~ s/&gt;&gt;(\d)([\d\-]*)/<a href=\"$script?mode=view2&f=$f&no=$1$2\" target=\"_blank\">&gt;&gt;$1$2<\/a>/gi;
# ���X���Q�� by �����
#	$msg =~ s/&gt;&gt;\[(\d+)\](-?)([\d]?)([\d\-]*)([^<&]*)/<a href=\"$script?mode=view&no=$1&l=$3$4\" target=\"_blank\">&gt;&gt;[$1]$2$3$4$5<\/a>/gi;
	if ($showthreadno) {
	$msg =~ s/&gt;&gt;\[(\d+)\](-)([\d]?)([\d\-]*)([^<&]*)/<a href=\"$readcgi?no=$1&l=$3$4\" target=\"$target\">&gt;&gt;[$1]$2$3$4$5<\/a>/gi;
	$msg =~ s/&gt;&gt;\[(\d+)\]([^\-][^<&\-]*)/<a href=\"$readcgi?no=$1\" target=\"$target\">&gt;&gt;[$1]$2<\/a>/gi;
	}
# ���X���Q�Ɓi�X�����Q�Ƃ���݂̂̊ȈՔŁE�\���n���������̂��߁j
#	$msg =~ s/&gt;&gt;\[(\d+)\]([^<&]*)/<a href=\"$readcgi?no=$1\" target=\"$target\">&gt;&gt;[$1]$2<\/a>$3/gi;
# bctp�����N �iBitComet�p�j
#	$msg =~ s/([^=^\"]|^)(bctp\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,\|]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
# bc�����N �iBitComet 0.87�ȍ~�p�j
#	$msg =~ s/([^=^\"]|^)(bc\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
# ����T�C�g���̋����̒���URL�w���u���i�\���͂��̂܂܂̂���j
	$msg =~ s/\"($fullscript\?)mode=view\&amp\;([^\&]*)/\"$1$2/g;
# ����T�C�g���̃����N�� nofollow ����
#	$msg =~ s/<a href=\"($fullscript)([\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]*)\" ([^\s]*) rel=\"nofollow\">/<a href=\"$1$2\" $3>/g;
	$msg =~ s/<a href=\"($home)([\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]*)\" (.*) rel=\"nofollow\">/<a href=\"$1$2\" $3>/g;
# ���Ƃ��Ƃ� >> �����N�����i����L�����j
#$msg =~ s/&gt;&gt;([0-9]?[0-9]?[0-9]?)/<a href=\"$readcgi?no=$f&l=1-1000#$1\">&gt;&gt;$1$2<\/a>/gi;
$msg =~ s/&gt;&gt;([0-9]?[0-9]?[0-9]?)/<a href=\"#\" class=\"scroll\" name="\d$1\">&gt;&gt;$1<\/a>/gi;

#	$msg =~ s/&gt;&gt;\[([\d]+)&gt;([\d]+)\]/<a href=\"$readcgi?mode=view2&f=$1&no=$2\" target=\"$target\">&gt;&gt;\[$1&gt;$2\]<\/a>/gi;
# URL��Z���������߃R����OK
#	$msg =~ s/&gt;&gt;(\d)([\d\-]*)/<a href=\"$readcgi?no=$in{'no'}&l=$1$2\" target=\"$target\">&gt;&gt;$1$2<\/a>/gi;

	# �X�}�C���摜�ϊ�
	if ($smile) {
		local($tmp);
		foreach (0 .. $#s1) {
			$tmp = $s2[$_];
			$tmp =~ s/([\+\*\.\?\^\$\[\-\]\|\(\)\\])/\\$1/g;
			$msg =~ s/$tmp/ <img src=\"$imgurl\/$s1[$_]\">/g;
		}
	}
	$msg;
}

#-------------------------------------------------
#  �摜���T�C�Y
#-------------------------------------------------
sub resize {
	local($w,$h) = @_;

	# �����`�F�b�N
	if(int($w) == 0 || int($h) == 0) {
		return (0,0);
	}

	# �摜�\�� �g��/�k��
	if ($w != $img_max_w || $h != $img_max_h) {
		# ���ӂ̊g�k�����v�Z���A�Z�ӂ̊g�k���Ƃ��Ă��g�p����
		local $key;
		if ($w > $h) {
			$key = $img_max_w / $w;
		} else {
			$key = $img_max_h / $h;
		}

		$w = int ($w * $key) || 1;
		$h = int ($h * $key) || 1;
	}
	return ($w,$h);
}

#-------------------------------------------------
#  ���[���t�H�[���i���[�U�[�ԁj
#-------------------------------------------------
sub mailform {
	if ($ReadOnly) {
		&error("${Oshirase}���[���̑��M���ł��܂���B");
	}

	if (!$usermail) {
		&error("���[�U�[�Ԃ̃��[�����M�@�\\�͖����ɂȂ��Ă��܂��B");
	}

	# �񍐎�ʔ���
	# 1: �R�����g��  2: �ᔽ�X���b�h��  3: �x���X���b�h��
	my $type = exists($in{'type'}) ? int($in{'type'}) : 0;
	if ($type < 1 || $type > 3 || ($type == 1 && !exists($in{'no'}))) {
		error("�s���ȃA�N�Z�X�ł�");
	}

	# �Ώۃ��XNo����
	my $target_res_no = $in{'type'} == 1 ? int($in{'no'}) : 1;

	# mail.log ��������
	## �z�X�g��UserAgent�𔻒肷�郆�[�U�[�ł��邩�ǂ���(���O�Ώۂł͂Ȃ����ǂ���)�𔻒�
	my $same_host_ua_judge = 1;
	foreach my $exclude_host (@ngthread_thread_list_creator_name_override_exclude_hosts) {
		if (index($host, $exclude_host) >= 0) {
			$same_host_ua_judge = 0;
			last;
		}
	}
	## mail.log �A�����M�����E���ꃌ�X�A���񍐐�������
	open(my $maillog_fh, '<', $mailfile) || error("Open Error: $mailfile");
	flock($maillog_fh, 1) || error("Lock Error: $mailfile");
	while (<$maillog_fh>) {
		chomp($_);
		my ($maillog_thread_num, $maillog_res_num, $maillog_host, $maillog_useragent,
			$maillog_cookiea, $maillog_userid, $maillog_history_id, $maillog_time) = split(/<>/, $_);
		# $usermail_time_of_continuously_send_restricting���o�߂������O�s�͐���������s��Ȃ�
		if ($maillog_time + $usermail_time_of_continuously_send_restricting <= $time) {
			next;
		}

		# ���ꃆ�[�U�[�̏ꍇ�̂݁A����������s��
		if (($same_host_ua_judge && $maillog_host eq $host && $maillog_useragent eq $useragent)
			|| $maillog_cookiea eq $cookie_a
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
	}
	close($maillog_fh);

	# �X���b�h���O�t�@�C���I�[�v��
	my $thread_logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(my $threadlog_fh, '<', $thread_logfile_path) || error("Open Error: $in{'f'}.cgi");
	flock($threadlog_fh, 1) || error("Lock Error: $in{'f'}.cgi");

	# �X���b�h���O�t�@�C���擪�s���擾���A�X���b�h���E���X�����擾
	my $top = <$threadlog_fh>;
	chomp($top);
	my ($sub, $num_of_res) = (split(/<>/, $top))[1, 2];
	$sub =~ s/\0*//g;  # �X���b�h���Ɋ܂܂�Ă���null����(\0)���폜
	if ($num_of_res == 0) {
		$num_of_res = 1;
	}

	# �R�����g�񍐂̏ꍇ�A���݂��郌�X�ł��邩�ǂ����̃`�F�b�N���s���A���O�E�z�X�g���E�R�����g���擾����
	# ����ȊO�̕񍐂̏ꍇ�́A�擪�̃��X�̖��O�E�z�X�g���E�R�����g���擾����
	my ($res_name, $res_comment, $res_host);
	my $found_flg;
	if ($type != 1 || $target_res_no <= $num_of_res) {
		while (<$threadlog_fh>) {
			chomp($_);
			my @res = split(/<>/, $_);
			if ($type != 1 || $res[0] == $target_res_no) {
				($res_name, $res_comment, $res_host) = @res[2, 4, 6];
				$found_flg = 1;
				last;
			} elsif ($res[0] > $target_res_no) {
				last;
			}
		}
	}
	if (!$found_flg) {
		error("�Y�����郌�X��������܂���");
	}

	# �X���b�h���O�t�@�C���N���[�Y
	close($threadlog_fh);

	# ���[���t�H�[���ɕ\�����鈶�惁�[���A�h���X(*�Œu������������)
	my $to_eml_asterisk = $usermail_to_address;
	$to_eml_asterisk =~ s/./*/g;

	# �N�b�L�[�擾
	my ($cnam) = &get_cookie;

	# �񍐎�� �t�H�[���^�C�g���E������ �z���`
	my @form_contents = (
		undef, # dummy
		["[�R�����g��]", "�R�����g�񍐂ł��B<br>\nCCCCCC<br>\nCCCCCC\n"],
		["[�ᔽ�X���b�h��]", "�ᔽ�X���b�h�񍐂ł��B<br>\nBBBBB<br>\nBBBBB\n"],
		["[�x���X���b�h��]", "�x���X���b�h�񍐂ł��B<br>\nAAAAA<br>\nAAAAA\n"]
	);

	&header("���[�����M�t�H�[��");

	print <<"EOM";
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<Table border=0 cellspacing=0 cellpadding=0 width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border=0 cellspacing=0 cellpadding=5 width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/mail.gif" align="top">
&nbsp; <b>���[���t�H�[��${$form_contents[$type]}[0]</b></td>
<td align="right" bgcolor="$col3" nowrapper-main>
<a href="javascript:history.back()">�O��ʂɖ߂�</a></td>
</tr></table></Td></Tr></Table>

${$form_contents[$type]}[1]

<form action="$registcgi" method="post" name="myFORM" id="postform">
<input type="hidden" name="mode" value="mail">
<input type="hidden" name="job" value="send">
<input type="hidden" name="type" value="$type">
<input type="hidden" name="pm">
<input type="hidden" name="f" value="$in{'f'}">
EOM

	# �R�����g�񍐎��̂݃��XNo�𑗐M
	if ($type == 1) {
		print "<input type=\"hidden\" name=\"no\" value=\"$target_res_no\">\n";
	}

	print <<"EOM";
<Table border=0 cellspacing=0 cellpadding=0 width="100%">
<Tr><Td bgcolor="$col1">
<table border=0 cellspacing=0 cellpadding=5 width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>����</td>
  <td><input type="text" size=30 value="$res_name" maxlength=20 disabled></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>����A�h���X</td>
  <td><input type="text" size=30 value="$to_eml_asterisk" disabled> �i��\\���j
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>����</td>
  <td><input type="text" size=$sublength value="$sub" maxlength=$sublength disabled></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>���o�l</td>
  <td><input type="text" name="name" size=30 value="$cnam" maxlength=20></td>
</tr>
EOM

	# ��ރv���_�E�����j���[
	if ($type != 3) {
		print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>���</td>
  <td>
    <select name="category">
  	  <option value="-" selected>-</option>
  	  <option value="�l���">�l���</option>
  	  <option value="�ƍߗ\\��">�ƍߗ\\��</option>
  </td>
</tr>
EOM
	}

	# ���e�L�[
	if ($regist_key_res) {
		# �L�[����
		require $regkeypl;
		my ($str_plain, $str_crypt) = &pcp_makekey;

		# ���̓t�H�[��
		print qq |<tr bgcolor="$col2"><th bgcolor="$col2" width="100">���e�L�[(�K�{)</th>|;
		print qq |<td bgcolor="$col2"><input type="text" name="regikey" size="6" style="ime-mode:inactive">\n|;
		print qq |�i���e��4���̐���" <img src="$registkeycgi?$str_crypt" align="absmiddle" alt="���e�L�[">" ����͂��Ă��������j<a href="$registkeycgi?$str_crypt" target="_blank">�����������Ȃ��ꍇ��������N���b�N</a></td></tr>\n|;
		print qq |<input type="hidden" name="str_crypt" value="$str_crypt">\n|;
	}

	print <<"EOM";
</select></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80>�{��</td>
  <td bgcolor="$col2">
EOM

	$res_comment =~ s/<br>/\r/g;
	print <<"EOM";
���̕��́i���M����܂��j<br>
<textarea cols=$cols rows=$rows wrapper-main=soft disabled>$res_comment</textarea><br>
���[���{���i���M����܂��j<br>
<textarea name=comment cols=$cols rows=$rows wrapper-main=soft></textarea></td></tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="submit" value="���[���𑗐M����"> �����[���͘A�����đ��M�ł��܂���̂ł悭���e���m�F���Ă��������B</td>
  </form></tr></table>
</Td></Tr></Table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �v���r���[
#-------------------------------------------------
sub preview {
	if ($ReadOnly) {
		&error("$Oshirase");
	}

	# �����`�F�b�N
	if ($authkey && $my_rank < 2) {
		&error("���e�̌���������܂���");
	}

	# �w�b�_
	if ($smile) { &header("�V�K�X���b�h�쐬�v���r���[", "js"); }
	else { &header("�V�K�X���b�h�쐬�v���r���["); }

	print <<"EOM";
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%">
<tr>
  <td align="left" nowrapper-main>
	<a href="$bbscgi?">�g�b�v�y�[�W</a> &gt; �V�K�X���b�h�쐬�i�v���r���[�j
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>���e���m�F���ă^�C�g����ݒ肵�Ă�������</b></td>
</tr></table></Td></Tr></Table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td>
<font color="$col4"><br>
EOM

# �v���`�F�b�N
	# �R�����g�������`�F�b�N
	if (length($i_com) > $max_msg*2) {
		print "�������I�[�o�[�ł��B<br>�S�p$max_msg�����ȓ��ŋL�q���Ă�������<br>\n";
	}

	# �����`�F�b�N
	$in{'res'} =~ s/\D//g;

	# ���e���e�`�F�b�N
	if ($i_com eq "") { print "�R�����g�̓��e������܂���<br>\n"; }
	if ($i_nam eq "") {
		if ($in_name) { print "���O�͋L���K�{�ł�<br>\n"; }
		else { $i_nam = '������'; }
	}
	if ($in_mail == 1 && $in{'email'} eq "") { print "E-mail�͋L���K�{�ł�<br>\n"; }
	if ($in_mail == 2 && $in{'email'} ne "") { print "E-mail�͓��͋֎~�ł�<br>\n"; }
	if ($in_mail == 3 && $in{'email'} ne "") { print "E-mail�͓��͋֎~�ł�<br>\n"; }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		print "E-mail�̓��͓��e���s���ł�<br>\n";
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { print "���O�͐������L�����Ă�������<br>\n"; }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { print "�R�����g�͐������L�����Ă�������<br>\n"; }
	if ($in_pwd && $in{'pwd'} eq "") { print "�p�X���[�h�͓��͕K�{�ł�<br>\n"; }
	if (length($in{'pwd'}) > 8) { print "�p�X���[�h��8�����ȓ��ɂ��ĉ�����<br>\n"; }
	if ($webprotect_auth_new && $in{'user_id'} eq "") { print "�o�^ID�͓��͕K�{�ł�<br>\n"; }
	if ($webprotect_auth_new && $in{'user_pwd'} eq "") { print "�o�^�p�X���[�h�͓��͕K�{�ł�<br>\n"; }

	# ���e�L�[�`�F�b�N
	if ($regist_key_new) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			print "���e�L�[�����͕s���ł��B������Ă��鐔������͂��Ă�������<br>\n";
		}

		# ���e�L�[�`�F�b�N
		# -1 : �L�[�s��v
		#  0 : �������ԃI�[�o�[
		#  1 : �L�[��v
	}

	print <<"EOM";
</font>
</Td></Tr></Table>
EOM

	&form2("preview");

	print "</div><!-- �I�� container --></body></html>\n";
	exit;
}

#-------------------------------------------------
#  �v���r���[�i���X�p�j
#-------------------------------------------------
sub resview {

	# �w�b�_
	if ($smile) { &header("�ԐM�v���r���[", "js"); }
	else { &header("�ԐM�v���r���["); }

	print <<"EOM";
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%">
<tr>
  <td align="left" nowrapper-main>
	<a href="$bbscgi?">�g�b�v�y�[�W</a> &gt; <a href=\"$readcgi?no=$in{'res'}\">�X���ɖ߂�</a> &gt; �ԐM�i�v���r���[�j
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>���e���m�F���ă^�C�g����ݒ肵�Ă�������</b></td>
</tr></table></Td></Tr></Table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td>
<font color="$col4"><br>
EOM

# �v���`�F�b�N
	# �R�����g�������`�F�b�N
	if (length($i_com) > $max_msg*2) {
		print "�������I�[�o�[�ł��B<br>�S�p$max_msg�����ȓ��ŋL�q���Ă�������<br>\n";
	}

	# �����`�F�b�N
	$in{'res'} =~ s/\D//g;

	# �X���b�h���O��擪2�s�ǂݍ���
	my @log;
	{
		my $logfile_path = get_logfolder_path($in{'res'}) . "/$in{'res'}.cgi";
		open(my $log_fh, $logfile_path) || &error("Open Error: $in{'res'}.cgi");
		flock($log_fh, 1) || &error("Lock Error: $in{'res'}.cgi");
		for (my $i=0; $i<2; $i++) {
			my $line = <$log_fh>;
			chomp($line);
			push(@log, [split(/<>/, $line)]);
		}
		close($log_fh);
	}

	# �X���b�h�^�C�g���ǂݍ���
	my $sub = ${$log[0]}[1];
	$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

	# �e���X�ǂݍ���
	my ($ho,$url,$user_id,$cookie_a,$history_id) = @{$log[1]}[6,8,16,18,19];

	# �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\�̃X���b�h�쐬�҂̏��O�@�\
	# >>1�� �z�X�g, URL��, �o�^ID, CookieA, ����ID ���擾
	my %first_res = (
		'host'       => $ho,
		'url'        => $url,
		'user_id'    => $user_id,
		'cookie_a'   => $cookie_a,
		'history_id' => $history_id,
	);

	# ���e���e�`�F�b�N
	if ($i_com eq "") { print "�R�����g�̓��e������܂���<br>\n"; }
	if ($i_nam eq "") {
		if ($in_name) { print "���O�͋L���K�{�ł�<br>\n"; }
		else { $i_nam = '������'; }
	}
	if ($in_mail == 1 && $in{'email'} eq "") { print "E-mail�͋L���K�{�ł�<br>\n"; }
	if ($in_mail == 2 && $in{'email'} ne "") { print "E-mail�͓��͋֎~�ł�<br>\n"; }
	if ($in_mail == 3 && $in{'email'} ne "") { print "E-mail�͓��͋֎~�ł�<br>\n"; }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		print "E-mail�̓��͓��e���s���ł�<br>\n";
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { print "���O�͐������L�����Ă�������<br>\n"; }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { print "�R�����g�͐������L�����Ă�������<br>\n"; }
	if ($in_pwd && $in{'pwd'} eq "") { print "�p�X���[�h�͓��͕K�{�ł�<br>\n"; }
	if (length($in{'pwd'}) > 8) { print "�p�X���[�h��8�����ȓ��ɂ��ĉ�����<br>\n"; }
	if ($webprotect_auth_res && $in{'user_id'} eq "") { print "�o�^ID�͓��͕K�{�ł�<br>\n"; }
	if ($webprotect_auth_res && $in{'user_pwd'} eq "") { print "�o�^�p�X���[�h�͓��͕K�{�ł�<br>\n"; }

	# ���e�L�[�`�F�b�N
	if ($regist_key_res) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			print "���e�L�[�����͕s���ł��B������Ă��鐔������͂��Ă�������<br>\n";
		}

		# ���e�L�[�`�F�b�N
		# -1 : �L�[�s��v
		#  0 : �������ԃI�[�o�[
		#  1 : �L�[��v
	}

	print <<"EOM";
</font>
</Td></Tr></Table>
EOM

	&form2("resview", $sub, \%first_res);

	print "</div><!-- �I�� container --></body></html>\n";

	exit;
}

# NG�l�[���@�\���p����NG���X���e�Җ��\���J�b�g�@�\�Ŏg�p���܂�
# �\�������E�J�b�g���������ꂼ�ꕪ���ă��X�g�Ƃ��ĕԂ��܂�
sub cut_name {
	my ($orig_name) = @_;
	my ($disp_name, $cut_name);

	if($ngname_dispchar_length > 0) {
		my $utf8flagged_name = $enc_cp932->decode($orig_name);
		my $utf8flagged_name_length = length($utf8flagged_name);
		my $disp_name_length = List::Util::min($utf8flagged_name_length, $ngname_dispchar_length);

		if($disp_name_length == $utf8flagged_name_length) {
			$disp_name = $orig_name;
		} else {
			$disp_name = $enc_cp932->encode(substr($utf8flagged_name, 0, $disp_name_length));
			$cut_name = $enc_cp932->encode(substr($utf8flagged_name, $disp_name_length));
		}
	} elsif($ngname_dispchar_length == 0) {
		$cut_name = $orig_name;
	} else {
		$disp_name = $orig_name;
	}

	if($cut_name ne "") {
		$cut_name = "<span class=\"cut_name\">${cut_name}</span>";
	}

	return ($disp_name, $cut_name);
}

# NG���[�h�@�\��Cookie�Z�b�g�Ŏg�p���܂�
sub set_ngword_cookie {
	# ���s�R�[�h��LF�œ���
	$in{'ngwords'} =~ s/\r\n/\n/g;
	$in{'ngwords'} =~ s/\r/\n/g;

	# �������̎Q�Ƃ��f�R�[�h
	$in{'ngwords'} = HTML::Entities::decode($in{'ngwords'});

	# UTF8�t���O�t�������ɕϊ���ALF��split���A��s�̗v�f���폜
	my @ngwords = grep { $_ ne '' } split(/\n/, $enc_cp932->decode($in{'ngwords'}));

	if (defined($chistory_id)) {
		# ����ID�ɕۑ�
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngword_settings(\@ngwords);
		$history_log->DESTROY();
	} else {
		# Cookie������
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGWORD_LIST";

		# �v�f����1�ȏ゠��ꍇ�̓Z�b�g���A�����łȂ��ꍇ��Cookie���폜
		if (scalar(@ngwords) > 0) {
			# JSON�`���ɕϊ���AURL�G���R�[�h
			my $urlencoded_json_ngwords = JSON::XS->new->utf8(1)->encode(\@ngwords);
			$urlencoded_json_ngwords =~ s/(\W)/'%' . unpack('H2', $1)/eg;
			$urlencoded_json_ngwords =~ s/\s/+/g;

			# Cookie�T�C�Y����
			if(length($cookie_name . $urlencoded_json_ngwords) > 4093) {
				error("�������I�[�o�[�ł��B");
			}

			# Cookie�Z�b�g
			print "Set-Cookie: $cookie_name=$urlencoded_json_ngwords; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
		} else {
			# Cookie�폜
			print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
		}
	}

	# �������b�Z�[�W�\��
	success("NG���[�h�ݒ肵�܂����B");
}

# �A��NG�@�\��Cookie�Z�b�g�Ŏg�p���܂�
sub set_chain_ng {
	# �A��NG�@�\ �t���O�擾
	my $flg = $chain_ng; # �f�t�H���g�l��\�ߎ擾
	if(exists($in{'chainng'}) && ($in{'chainng'} eq "0" || $in{'chainng'} eq "1")) {
		$flg = $in{'chainng'};
	}

	if (defined($chistory_id)) {
		# ����ID�ɕۑ�
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_chain_ng_setting($flg);
		$history_log->DESTROY();
	} else {
		# Cookie�Z�b�g
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_CHAIN_NG";
		print "Set-Cookie: $cookie_name=$flg; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
	}

	# �������b�Z�[�W�\��
	success("�A����" . ($flg ? "�L��" : "����") . "�ɐݒ肵�܂����B");
}

# �����̓��e��ڗ�������@�\�̐ݒ�擾�Ŏg�p���܂�
sub get_highlight_name_on_own_post {
	my $ret_val = 1; # ���ݒ莞�͗L��
	if (defined($chistory_id)) {
		# ����ID���O����擾
		my $instance = HistoryLog->new($chistory_id);
		if ((my $flg = $instance->get_highlight_name_active_flag()) >= 0) {
			# ����ID���O�ɕۑ�����Ă��鎞�͂��̃t���O���擾
			$ret_val = $flg;
		}
		$instance->DESTROY();
	} else {
		# Cookie����擾
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_HIGHLIGHT_NAME";
		foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
			my ($name, $value) = split(/=/, $cookie_set);
			if ($name eq $cookie_name) {
				# Cookie�ɕۑ�����Ă���Ƃ��͂��̒l���m���߂���Ńt���O���擾
				if ($value eq '1' || $value eq '0') {
					$ret_val = int($value);
				}
				last;
			}
		}
	}
	return $ret_val;
}

# �����̓��e��ڗ�������@�\�̐ݒ�Ŏg�p���܂�
sub set_highlight_name_on_own_post {
	# �t���O�擾
	my $flg = 1;
	if(exists($in{'highlightname'}) && ($in{'highlightname'} eq "0" || $in{'highlightname'} eq "1")) {
		$flg = int($in{'highlightname'});
	} else {
		error("�����̓��e��ڗ��������ݒ�ł��܂���ł����B");
	}

	if (defined($chistory_id)) {
		# ����ID�ɕۑ�
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_highlight_name_active_flag($flg);
		$history_log->DESTROY();
	} else {
		# Cookie�Z�b�g
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_HIGHLIGHT_NAME";
		print "Set-Cookie: $cookie_name=$flg; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
	}

	# �������b�Z�[�W�\��
	my $back_url = '';
	if (exists($in{'no'})) {
		$back_url = "$readcgi?no=$in{'no'}";
		if (exists($in{'p'})) {
			$back_url .= "&p=$in{'p'}";
		}
		if (exists($in{'l'})) {
			$back_url .= "&l=$in{'l'}";
		}
	}
	success("�ڗ��������" . ($flg ? "�L��" : "����") . "�ɐݒ肵�܂����B", $back_url);
}

# �o�^����NG�l�[���̈ꊇ�폜�Ŏg�p���܂�
sub clear_ngname {
	if (defined($chistory_id)) {
		# ����ID�ɕۑ�
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngname_settings();
		$history_log->DESTROY();
	} else {
		# Cookie�폜
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGNAME_LIST";
		print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
	}

	# �������b�Z�[�W�\��
	success("�o�^����NG�l�[����S�č폜���܂����B");
}

# �o�^����NGID�̈ꊇ�폜�Ŏg�p���܂�
sub clear_ngid {
	if (defined($chistory_id)) {
		# ����ID�ɕۑ�
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngid_settings();
		$history_log->DESTROY();
	} else {
		# Cookie�폜
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGID_LIST";
		print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
	}

	# �������b�Z�[�W�\��
	success("�o�^����NGID��S�č폜���܂����B");
}

# �\�����e����@�\�̕��򔻒�
sub judge_branch_contents {
	# ���������O�s���J�����ŕ��������z�񃊃t�@�����X�A
	# �������́A�X�J���[�ϐ��ł��邩�ǂ���
	my ($subject_or_reslogArrayRef) = @_;
	my $is_res_log_array_reference = ref($subject_or_reslogArrayRef) eq 'ARRAY';
	if ($is_branching_contents || (!$is_res_log_array_reference && ref($subject_or_reslogArrayRef) ne '')) {
		return;
	}
	# �\�����e����@�\ �������v����
	my @decoded_targets = do {
		if ($is_res_log_array_reference) {
			# ���O�s���J�����ŕ��������z�񃊃t�@�����X
			# ${$subject_or_reslogArrayRef}[2] -> ���O  ${$subject_or_reslogArrayRef}[4] -> ���X���e
			($enc_cp932->decode(${$subject_or_reslogArrayRef}[2]), $enc_cp932->decode(${$subject_or_reslogArrayRef}[4]));
		} else {
			# �X���b�h�^�C�g��
			($enc_cp932->decode($subject_or_reslogArrayRef));
		}
	};
	foreach my $decoded_keyword (@decoded_contents_branching_keyword) {
		# �ݒ肵����������܂�ł��邩�ǂ���
		foreach my $decoded_target (@decoded_targets) {
			if (index($decoded_target, $decoded_keyword) > -1) {
				$is_branching_contents = 1;
				return;
			}
		}
	}

	# �\�����e����@�\ �摜���܂�ł��邩�ǂ��� (�������X���b�h�^�C�g���̎��͔�����s��Ȃ�)
	if ($is_res_log_array_reference && $contents_branching_img_check
			&& ((split(/,/, ${$subject_or_reslogArrayRef}[12]))[0] ne ''
				|| (split(/,/, ${$subject_or_reslogArrayRef}[13]))[0] ne ''
				|| (split(/,/, ${$subject_or_reslogArrayRef}[14]))[0] ne ''
				)
		) {
		$is_branching_contents = 1;
	}
}

# �X���b�h��ʂ��烆�[�U�[�𐧌�����@�\ HTML�쐬
sub create_restrict_user_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# a�^�O�̑����l���쐬
	my $a_attr_html = '';
	foreach my $target_pair_ref (['cookie_a', $cookie_a], ['history_id', $history_id], ['host', $host], ['user_id', $user_id]) {
		my ($name, $value) = @{$target_pair_ref};
		if (!defined($value) || $value eq '') {
			next;
		}
		$a_attr_html .= " $name=\"$value\"";
	}
	if ($a_attr_html eq '') {
		return '';
	}

	# HTML���쐬���A�Ԃ�
	return <<"EOC";
EOC
}

# �X���b�h��ʂ��烆�[�U�[�����Ԑ�������@�\ HTML�쐬
sub create_restrict_user_by_time_range_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# a�^�O�̑����l���쐬
	my $a_attr_html = '';
	foreach my $target_pair_ref (['cookie_a', $cookie_a], ['history_id', $history_id], ['host', $host], ['user_id', $user_id]) {
		my ($name, $value) = @{$target_pair_ref};
		if (!defined($value) || $value eq '') {
			next;
		}
		$a_attr_html .= " $name=\"$value\"";
	}
	if ($a_attr_html eq '') {
		return '';
	}

	# HTML���쐬���A�Ԃ�
	return <<"EOC";
EOC
}

# �X���b�h��ʂ��烆�[�U�[�𐧌�����@�\ (���̃X���̂�) HTML�쐬
sub create_in_thread_only_restrict_user_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# a�^�O�̑����l���쐬
	my $a_attr_html = '';
	foreach my $target_pair_ref (['cookie_a', $cookie_a], ['history_id', $history_id], ['host', $host], ['user_id', $user_id]) {
		my ($name, $value) = @{$target_pair_ref};
		if (!defined($value) || $value eq '') {
			next;
		}
		$a_attr_html .= " $name=\"$value\"";
	}
	if ($a_attr_html ne '') {
		# �擪�ɃX���b�hNo��t��
		$a_attr_html = ' thread_num="' . int($in{'no'}) . '"' . $a_attr_html;
	} else {
		return '';
	}

	# HTML���쐬���A�Ԃ�
	return <<"EOC";
EOC
}

# ���[�U�[�����\���@�\ �o�^�E�폜�t�H�[��HTML�쐬
sub create_highlight_userinfo_form_html {
    my ($res_cookie_a, $res_history_id, $res_host, $res_user_id) = @_;

    # �o�^�{�^���E�폜�����N���ʂŒǉ�����A���[�U�[��񑮐����쐬
    my $userinfo_attr = '';
    foreach my $target_pair_ref (['cookie_a', $res_cookie_a], ['history_id', $res_history_id], ['host', $res_host], ['user_id', $res_user_id]) {
        my ($name, $value) = @{$target_pair_ref};
        if (!defined($value) || $value eq '') {
            next;
        }
        $userinfo_attr .= " $name=\"$value\"";
    }

#    # select�^�O�E�F����option�^�O���쐬
#    my $select_option_html = "<select class=\"highlight_userinfo_color\">\n";
#    for (my $i = 0; $i < scalar(@highlight_userinfo_color_name_code); $i++) {
#        my $color_number = $i + 1;
#        $select_option_html .= "\t<option value=\"$color_number\">�l$color_number�F${$highlight_userinfo_color_name_code[$i]}[0]</option>\n";
#    }
#    $select_option_html .= "</select>";

    # HTML���쐬���A�Ԃ�
#    return <<"EOC";
#$select_option_html
#<button type="button" class="highlight_userinfo_add"$userinfo_attr>�o�^</button>
#<span class="highlight_userinfo_ajax_message highlight_userinfo_add_ajax_message"></span>
#&nbsp;&nbsp;
#<a href="#" class="highlight_userinfo_remove"$userinfo_attr>�폜</a>
#<span class="highlight_userinfo_ajax_message highlight_userinfo_remove_ajax_message"></span>
#EOC
}

1;
