#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� find.pl - 2007/04/09
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# 2011/07/29 �R�����g�A�E�g�̃o�O�C��
# 2011/04/27 �召���ꎋ�̃o�O�C��
# 2010/10/19 �{�������̊ȑf���R�[�h����荞��
# 2010/01/11 �g�s�b�N�X�����O���`�F�b�N���Ȃ��ƌ��������s����Ȃ��̂��C��
# 2009/12/07 �y�[�W����̃����N�ɃI�v�V���������f����Ă��Ȃ�����
# 2009/07/02 �L�^���e�ɃX�^�[�g�A������ǉ�
# 2009/06/01 FAQ���[�h�̕\���ɑΉ�
# 2007/05/10 �{���������Ώۂ�

#-------------------------------------------------
#  ���[�h����
#-------------------------------------------------
BEGIN {
	require './init.cgi';
}
use Time::Piece;
use Time::Seconds;
use LWP::UserAgent;
use JSON::XS;
use URI;
use if $find_recaptcha_continue == 1, 'JSON::WebEncryption';


my $find_cookie_name;
my $json_webencryption_instance;

if ($find_recaptcha_continue) {
	# �Z�b�V����Cookie����`
	$find_cookie_name = "WEB_PATIO_${cookie_current_dirpath}_FIND_LIST";

	# JSON::WebEncryption �C���X�^���X�쐬
	$json_webencryption_instance = JSON::WebEncryption->new(
		'alg'         => 'RSA1_5',
		'enc'         => 'A256CBC-HS512',
		'private_key' => $find_recaptcha_continue_cookie_rsa_private_key,
		'public_key'  => $find_recaptcha_continue_cookie_rsa_public_key
	);
}

sub find {
	local($target,$alarm,$next,$back,$enwd,$imgfind,@log1,@log2,@log3,@wd,@imgfile_expr,@findtypes,$find_log_append_contents);

	# ������ʒ�`
	@findtypes = (["�L�[���[�h����", "keyword"], ["�o�^ID����", "user_id"], ["���[�UID����", "patio_id"]);

	# ���������s���邩�ǂ���
	my $performFinding = $in{'word'} && ($in{'type'} eq "keyword" && $in{'s'} || $in{'n'} || $in{'r'} || $in{'c'}) || $in{'type'} eq "user_id" || $in{'type'} eq "patio_id";

	# GET���\�b�h�ɂ��A�N�Z�X��
	if (!$postflag) {
		if ($performFinding) {
			# GET���\�b�h�Ō��������s�����ꍇ�́AURL�N���A�̂���301���_�C���N�g
			print "Status: 301 Moved Permanently\n";
			print "Location: " . URI->new("$bbscgi?mode=find")->abs($ENV{'REQUEST_URI'}) . "\n\n";
			exit(0);
		} else {
			# GET���\�b�h�ŁA�s���Ȍ����t�H�[���l���󂯎��Ȃ����߂ɏ�����
			undef(%in);
			$in{'mode'} = 'find';
		}
	}

	# �������s���̓y�[�W�Ԉړ��ł͂Ȃ��������ǂ���
	my $is_first_find = $performFinding && $in{'p'} eq '';

	# �����L�[���[�h�œK���E�������O�������ݕ�����쐬
	if ($performFinding) {
		$in{'word'} =~ s/\x81\x40/ /g;
		chomp($in{'word'});

		my $find_type;
		foreach (@findtypes) {
			if (${$_}[1] eq $in{'type'}) {
				$find_type = "${$_}[0]";
				last;
			}
		}

		$find_log_append_contents = "$date,$in{'word'},$in{'vw'},$host,$find_type,$time\n";
	}

	# reCAPTCHA�F��
	my $display_recaptcha_form = 0;
	if ($find_recaptcha || $in{'g-recaptcha-response'} ne '') {
		my $find_cookie;
		if ($find_recaptcha_continue) {
			# �Z�b�V����Cookie����ߋ��̌�����/�^�C���X�^���v��ǂݎ��
			$find_cookie = read_find_cookie();
			foreach my $word (keys(%{$find_cookie})) {
				# ��������A���������J�E���g���Ԃ��߂����^�C���X�^���v����������
				@{${$find_cookie}{$word}} = grep { $_ + $find_recaptcha_continue_count_time > $time } @{${$find_cookie}{$word}};
			}
		}

		# reCAPTCHA�F�ؕ\������
		my ($perform_recaptcha_auth, $find_log_fh, $auth_host_log_fh);
		if (!$performFinding) {
			# �����t�H�[���̂ݕ\����
			if (open($find_log_fh, '<', $find_recaptcha_count_log) && flock($find_log_fh, 1) # �����������O�I�[�v��
				&& open($auth_host_log_fh, '+>>', $find_recaptcha_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA�F�ؑΏۃz�X�g���O�I�[�v��
				# �����������O�s���J�E���g
				my $find_count = 0;
				while (sysread $find_log_fh, my $buffer, 4096) {
					$find_count += ($buffer =~ tr/\n//);
				}
				$find_count--; # �擪�s������������
				$display_recaptcha_form = $find_count + 1 > $find_recaptcha_permit; # �A���������e���𒴂��Č������悤�Ƃ��Ă��邽�߁AreCAPTCHA�F�؂�L��
				close($find_log_fh);

				# reCAPTCHA�F�ؑΏۃz�X�g���O��
				# �z�X�g����v����ꍇ�͍X�V�A����ȊO�ł��F�ؑΏۂ̏ꍇ�͒ǋL����
				my $auth_host_log = "����,������,�z�X�g,�^�C���X�^���v\n";
				<$auth_host_log_fh>; # �擪�s�ǂݔ�΂�
				while (<$auth_host_log_fh>) {
					chomp($_);
					my $log_host = (split(/,/, $_))[2];
					if ($log_host eq $host) {
						$display_recaptcha_form = 1;
					} else {
						$auth_host_log .= "$_\n";
					}
				}
				if ($. < 1 || $display_recaptcha_form) {
					if ($display_recaptcha_form) {
						$auth_host_log .= "$date,,$host,$time\n";
					}
					seek($auth_host_log_fh, 0, 0);
					truncate($auth_host_log_fh, 0);
					print $auth_host_log_fh $auth_host_log;
				}
				close($auth_host_log_fh);
			} else {
				error("Error: reCAPTCHA");
			}
		} else {
			# �������s��
			if (open($find_log_fh, '+>>', $find_recaptcha_count_log) && flock($find_log_fh, 2) && seek($find_log_fh, 0, 0) # �����������O�I�[�v��
				&& open($auth_host_log_fh, '+>>', $find_recaptcha_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA�F�ؑΏۃz�X�g���O�I�[�v��
				# reCAPTCHA���X�|���X�����M����Ă������́A�ݒ�ɂ�����炸�F�؂����{
				$perform_recaptcha_auth = $in{'g-recaptcha-response'} ne '';

				# �����������O�s���J�E���g�E�����Ώۍs���O
				my $find_log = "����,������,�\\������,�z�X�g,�������,�^�C���X�^���v\n";
				my $find_count = 0;
				my $delete_time_not_reached_find_count = 0;
				my $is_find_log_changed = 0;
				my $is_recaptcha_enabled_in_delete_log = 0;
				<$find_log_fh>; # �擪�s�ǂݔ�΂�
				while (<$find_log_fh>) {
					chomp($_);
					my @line = split(/,/, $_);
					if (scalar(@line) == 6) {
						# �����������������A�������Ԃ��o�߂��Ă��Ȃ����O�̂ݎc��
						if ($find_recaptcha_count_time == 0 || ($line[5] + $find_recaptcha_count_time >= $time)) {
							$find_log .= "$_\n";
							$delete_time_not_reached_find_count++;
						} else {
							$is_find_log_changed = 1;
						}
						$find_count++; # �J�E���g�͕ʂɍs��
					}
				}
				if ($. < 1) {
					$is_find_log_changed = 1;
				}
				$is_recaptcha_enabled_in_delete_log = $find_count + 1 > $find_recaptcha_permit; # �A���������e���𒴂��Č������悤�Ƃ��Ă���AreCAPTCHA�F�ؑΏۂ��ǂ���
				$perform_recaptcha_auth ||= $is_recaptcha_enabled_in_delete_log;
				$display_recaptcha_form ||= $delete_time_not_reached_find_count + 1 > $find_recaptcha_permit; # �������s��̘A�������������e���𒴂��āAreCAPTCHA�\���Ώۂ��ǂ���

				# reCAPTCHA�F�ؑΏۃz�X�g���O�m�F
				my $auth_host_log = "����,������,�z�X�g,�^�C���X�^���v\n";
				my $host_found_in_recaptcha_auth_log = 0;
				my $is_auth_host_log_changed = 0;
				<$auth_host_log_fh>; # �擪�s�ǂݔ�΂�
				while (<$auth_host_log_fh>) {
					chomp($_);
					my @line = split(/,/, $_);
					if (scalar(@line) == 4) {
						# ����z�X�g�������������A�F�ؑΏۂƂ���
						my $is_current_line_same_host = $line[2] eq $host;
						if ($is_current_line_same_host) {
							$perform_recaptcha_auth = 1;
							$host_found_in_recaptcha_auth_log = 1;
						}
						# �����������������A�������Ԃ��o�߂��Ă��Ȃ����O�̂ݎc��
						if ($find_recaptcha_auth_host_release_time == 0 || ($line[3] + $find_recaptcha_auth_host_release_time >= $time)) {
							if ($is_current_line_same_host) {
								$display_recaptcha_form = 1; # ����z�X�g�������������A�������Ԃ��o�߂��Ă��Ȃ����reCAPTCHA���ĕ\��
								$is_auth_host_log_changed = 1;
							} else {
								$auth_host_log .= "$_\n";
							}
						} else {
							$is_auth_host_log_changed = 1;
						}
					}
				}
				# reCAPTCHA�F�ؑΏۂɂȂ����z�X�g�����O�ɒǉ�
				if ($. < 1 || $display_recaptcha_form || ($is_recaptcha_enabled_in_delete_log && !$host_found_in_recaptcha_auth_log)) {
					if ($display_recaptcha_form || ($is_recaptcha_enabled_in_delete_log && !$host_found_in_recaptcha_auth_log)) {
						$auth_host_log .= "$date,$in{'word'},$host,$time\n";
					}
					$is_auth_host_log_changed = 1;
				}

				my $utf8flagged_find_word;
				if ($find_recaptcha_continue) {
					# ��������ł̃y�[�W�J�ڂɂ�錟�����s����reCAPTCHA�F�؃X�L�b�v����
					$utf8flagged_find_word = $enc_cp932->decode($in{'word'});
					my $skip_recaptcha_auth_by_page_moving = 0;
					if (!$is_first_find && exists(${$find_cookie}{$utf8flagged_find_word})) {
						$skip_recaptcha_auth_by_page_moving = scalar(@{${$find_cookie}{$utf8flagged_find_word}}) + 1 > $find_recaptcha_continue_permit;
						$perform_recaptcha_auth &&= $skip_recaptcha_auth_by_page_moving;
					}
				}

				# reCAPTCHA�F�؎��{
				if ($perform_recaptcha_auth) {
					# reCAPTCHA���\������Ȃ����A�`�F�b�N���s���Ă��Ȃ����Ȃ�
					# reCAPTCHA���X�|���X�����M����Ă��Ă��Ȃ����́AAPI�Ƃ̒ʐM���s��Ȃ�
					my $is_recaptcha_auth_success = 0;
					if ($in{'g-recaptcha-response'} ne '') {
						# reCAPCTHA API�ƒʐM
						my $lwp_ua = LWP::UserAgent->new(timeout => 2);
						my $lwp_response = $lwp_ua->post(
							'https://www.google.com/recaptcha/api/siteverify',
							[ secret => $recaptcha_secret_key, response => $in{'g-recaptcha-response'} ]
						);

						if ($lwp_response->is_success) {
							# ����ɒʐM���s�����ꍇ�ɂ̂ݔF�؏󋵂̊m�F���s��
							my $result = JSON::XS->new()->decode($lwp_response->content);
							my $is_bool = $JSON::XS::VERSION >= 3 ? \&Types::Serialiser::is_bool : \&JSON::XS::is_bool;
							if (${$result}{'success'} && $is_bool->(${$result}{'success'})) {
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
						if (!exists($in{'g-recaptcha-response'})) {
							# reCAPTCHA���X�|���X�t�B�[���h�������ꍇ�́A�����y�[�W�Ƀ����N
							error("�O��ʂɖ߂�A�y�[�W���ēǂݍ��݂��ĔF�؂��s���ĉ������B", "$bbscgi?mode=find");
						} else {
							# reCAPTCHA���\������Ă���y�[�W�������ꍇ�̓u���E�U�q�X�g���[�Ŗ߂�
							my $msg = "�F�؂Ɏ��s���Ă��邩�A�L���������؂�Ă��܂��B";
							if ($skip_recaptcha_auth_by_page_moving) {
								$msg .= "���������y�[�W�ړ����s���ꍇ�́A�F�؂��s������y�[�W�ړ������ĉ������B";
							}
							error($msg);
						}
					}
				}

				# �����������O�֏�������
				if ($is_find_log_changed) {
					seek($find_log_fh, 0, 0);
					truncate($find_log_fh, 0);
					print $find_log_fh $find_log;
				} elsif ($is_first_find) {
					seek($find_log_fh, 0, 2);
				}
				if ($is_first_find) {
					print $find_log_fh $find_log_append_contents;
				}
				close($find_log_fh);

				# reCAPTCHA�F�ؑΏۃz�X�g���O�֏�������
				if ($is_auth_host_log_changed) {
					seek($auth_host_log_fh, 0, 0);
					truncate($auth_host_log_fh, 0);
					print $auth_host_log_fh $auth_host_log;
				}
				close($auth_host_log_fh);

				# �������s���ɁA�Z�b�V����Cookie���e�ϐ��Ɍ�����/�^�C���X�^���v��ǉ�
				if ($find_recaptcha_continue) {
					push(@{${$find_cookie}{$utf8flagged_find_word}}, $time);
				}
			} else {
				error("Error: reCAPTCHA");
			}
		}

		if ($find_recaptcha_continue) {
			# �Z�b�V����Cookie�i�[�n�b�V������^�C���X�^���v��1���Ȃ���������폜
			foreach my $word (keys(%{$find_cookie})) {
				if (scalar(@{${$find_cookie}{$word}}) == 0) {
					delete(${$find_cookie}{$word});
				}
			}
			# �Z�b�V����Cookie�ɕۑ�
			# �ő�i�[�T�C�Y�𒴂��Ă���Ƃ��́A
			# �Ō�̌����������ł��Â���������̂Ă�
			while (set_find_cookie($find_cookie) != 1) {
				my ($oldest_time, $oldest_word) = ~0;
				foreach my $word (keys(%{$find_cookie})) {
					my $last_index = $#{${$find_cookie}{$word}};
					if (${${$find_cookie}{$word}}[$last_index] < $oldest_time) {
						$oldest_word = $word;
					}
				}
				delete(${$find_cookie}{$oldest_word});
			}
		}
	}

	# �ݐό������O��������
	if ($performFinding && $srchlog) {
		my $srchlog_fh;
		(open($srchlog_fh, '+>>', $srchlog) && flock($srchlog_fh, 2) && seek($srchlog_fh, 0, 0)) || error("Write Error: $srchlog");
		<$srchlog_fh>;
		if ($. < 1) {
			seek($srchlog_fh, 0, 0);
			truncate($srchlog_fh, 0);
			print $srchlog_fh "����,������,�\\������,�z�X�g,�������,�^�C���X�^���v\n";
		} elsif ($is_first_find) {
			seek($srchlog_fh, 0, 2);
		}
		if ($is_first_find) {
			print $srchlog_fh $find_log_append_contents;
		}
		close($srchlog_fh);
	}

	# �t�H�[�������l�⌟���Ŏg�p������t�������\�߃t�H�[�}�b�g����
	chomp($in{'dateFrom'});
	chomp($in{'dateTo'});
	if($in{'dateFrom'} !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) { $in{'dateFrom'} = "" }
	if($in{'dateTo'} !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) { $in{'dateTo'} = "" }

	&header();
	print <<"EOM";


<STYLE type="text/css">
<!--

*{
	margin:0px;
	padding:0px;
}





table#teeest{
  background-color:#ffffff;
/*  border: 1px solid #64bf64;	*/
  border-collapse: collapse;
  max-width:100%;
}

table#teeest tr{
/*  border: 1px solid #64bf64;	*/
}
table#teeest td {
  border-bottom: 1px solid #64bf64;
}

#wrapper-main-in-table{
	margin:20px;
}

blockquote{
	margin:10px 0px;
}


tr.test6 a,
tr.test7 a,
tr.test1 a,	/* �Ǘ��҃��b�N */
tr.test3 a,	/* 	�X���b�h�������O�}�[�N */
tr.test5 a,
td.test5 a {
	display:block;
	width:100%;
	color:#000000 !important;
	padding:10px;
}

p.thread{
}
p.thread a:link,
p.thread a:visited{
	color:#888888;
	padding:8px 0px 8px 6px;
	display:block;
	text-decoration:none;
}
/*
p.thread a:visited{
	color:#ff8c00;
}
*/


.td1{
	border-bottom:1px solid #cbcbcb;
	width:100%;
}
.td2{
	border-bottom:1px solid #cbcbcb;
	background-color:#fafafa;
}




-->
</STYLE>

<div align="center">
<table width="95%"><tr><td align="right" nowrap>
<a href="$bbscgi?">�g�b�v�y�[�W</a> &gt; ���[�h����
</td></tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/glass.gif" align="middle">
&nbsp;<b>���[�h����</b></td>
</tr></table></Td></Tr></Table>
<P>
<form action="$bbscgi?mode=find" method="post">
<input type="hidden" name="mode" value="find">
<input type="hidden" name="p" value="">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2"><td bgcolor="$col2">
�L�[���[�h <input type="text" name="word" size="38" value="$in{'word'}"> &nbsp;
���� <select name="op">
EOM

	foreach ("AND", "OR") {
		print "<option";
		if ($in{'op'} eq $_) {
			print " selected";
		}
		print ">$_</option>\n";
	}
	print "</select> &nbsp; NOT���� ";
	if($in{'not'}) {
		print "<input type=checkbox name=\"not\" value=\"1\" checked>";
	} else {
		print "<input type=checkbox name=\"not\" value=\"1\">";
	}
	print " &nbsp; �\\�� <select name=vw>\n";
	foreach (1,2,3,5,7,9,10,100,150,200,250) {
		if ($in{'vw'} == $_) {
			print "<option value=\"$_\" selected>$_��\n";
		} else {
			print "<option value=\"$_\">$_��\n";
		}
	}
	print "</select> �啶������������ʂ��Ȃ� <select name=cs>\n";
	foreach ("ON", "OFF") {
		if ($in{'cs'} eq $_) {
			print "<option value=\"$_\" selected>$_\n";
		} else {
			print "<option value=\"$_\">$_\n";
		}
	}
	print "</select><br>";

	print "<br>���Ԏw��(�ŏI��������) ";
	print "<input type=date name=\"dateFrom\" value=\"$in{'dateFrom'}\"> �` <input type=date name=\"dateTo\" value=\"$in{'dateTo'}\">";

	print "<br>�����͈� ";
	if ($in{'log'} eq "") { $in{'log'} = 2; }
	@log1 = ([$nowfile], [$pastfile], [$nowfile, $pastfile]);
	@log2 = ("���s���O", "�ߋ����O", "�ꊇ����");
	@log3 = ("view", "past", "cross");
	foreach (0..$#log2) {
		if ($in{'log'} == $_) {
			print "<input type=radio name=log value=\"$_\" checked>$log2[$_]\n";
		} else {
			print "<input type=radio name=log value=\"$_\">$log2[$_]\n";
		}
	}

	print "<br>������� ";
	if($in{'type'} ne "keyword" && $in{'type'} ne "user_id" && $in{'type'} ne "patio_id") {
		$in{'type'} = "keyword";
	}
	for(my $i=0; $i<scalar(@findtypes); $i++) {
		print "<input type=\"radio\" name=\"type\" value=\"${$findtypes[$i]}[1]\"";
		if(${$findtypes[$i]}[1] eq $in{'type'}) { print " checked=\"checked\""; }
		print ">${$findtypes[$i]}[0]";
	}

	print "<span id=\"findItem\"><br>�������� ";
	if ($in{'s'} eq "" && $in{'word'} eq "") { $in{'s'} = 1; }
	if ($in{'s'} == 1) {
		print "<input type=checkbox name=s value=\"1\" checked>�g�s�b�N�X\n";
	} else {
		print "<input type=checkbox name=s value=\"1\">�g�s�b�N�X\n";
	}
	if ($in{'n'} eq "" && $in{'word'} eq "") { $in{'n'} = 0; }
	if ($in{'n'} == 1) {
		print "<input type=checkbox name=n value=\"1\" checked>���O\n";
	} else {
		print "<input type=checkbox name=n value=\"1\">���O\n";
	}
	if ($in{'r'} eq "" && $in{'word'} eq "") { $in{'r'} = 1; }
	if ($in{'r'} == 1) {
		print "<input type=checkbox name=r value=\"1\" checked>���X�̃^�C�g��\n";
	} else {
		print "<input type=checkbox name=r value=\"1\">���X�̃^�C�g��\n";
	}

	if ($in{'c'} eq "" && $in{'word'} eq "") { $in{'c'} = 1; }
	if ($in{'c'} == 1) {
		print "<input type=checkbox name=c value=\"1\" checked>�{��\n";
	} else {
		print "<input type=checkbox name=c value=\"1\">�{��\n";
	}
	print "</span>";

	print <<EOM;
&nbsp;&nbsp;
<input type="submit" value="�������s" onclick=\"\$('input[name=p]').val(''); return true;\">
EOM
	if ($display_recaptcha_form) {
		print <<"EOM";
<br><br>
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
<div class="g-recaptcha" data-sitekey="${find_recaptcha_site_key}"></div>
<noscript>
    <div style="width: 302px; height: 422px;">
        <div style="width: 302px; height: 422px; position: relative;">
            <div style="width: 302px; height: 422px; position: absolute;">
                <iframe src="https://www.google.com/recaptcha/api/fallback?k=${find_recaptcha_site_key}"
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
	}
print <<EOM;
</td></tr></table>
</Td></Tr></Table>
</form>
EOM

	# �������s
	if ($performFinding) {

		# �A���[������`
		$alarm = int($m_max*0.9);

		# ���t�����͈͂��p�[�X
		my ($date_from, $date_to);
		if($in{'dateFrom'} !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) {
			$date_from = undef;
		} else {
			$date_from = localtime(Time::Piece->strptime($in{'dateFrom'}, '%Y-%m-%d'));
		}
		if($in{'dateTo'} !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) {
			$date_to = undef;
		} else {
			$date_to = localtime(Time::Piece->strptime($in{'dateTo'}, '%Y-%m-%d'));
		}
		if(defined($date_from) && defined($date_to) && $date_from > $date_to) {
			# ���ԓI��date_from���date_to���O�̏ꍇ�ɓ���ւ���
			($date_from, $date_to) = ($date_to, $date_from);
		}
		if(defined($date_to)) {
			# date_to�͂��̓���23:59:59�܂ł�ΏۂƂ���
			$date_to = $date_to + ONE_DAY - 1;
		}

		# ���t�͈͂���`����Ă���Δ͈͌������s��
		my $date_filter_hash = undef;
		if(defined($date_from) || defined($date_to)) {
			my $current_log_flg = $in{'log'} ne "1" ? 1 : 0;
			my $past_log_flg = $in{'log'} ne "0" ? 1 : 0;

			# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɐڑ����Ĕ͈͌���
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$date_filter_hash = $updatelog_db->find_threads_by_period($date_from, $date_to, $i_max * $current_log_flg, $p_max * $past_log_flg);
			$updatelog_db->close(0);
		}

		# �t�H�[���p�Ɍ����L�[���[�h��ޔ�
		$enwd = &url_enc($in{'word'});

		# �����L�[���[�h�𔼊p�X�y�[�X�ŕ���
		foreach my $encoded_wd (split(/\s+/, $in{'word'})) {
			# �����G���R�[�h�ɕϊ�
			my $decoded_wd = $enc_cp932->decode($encoded_wd);

			# �����L�[���[�h�z��ɒǉ�
			if ($in{'cs'} eq 'ON') {
				# �召��������ʂ��Ȃ����߁A��������������ɕϊ�
				push(@wd, lc($decoded_wd));
			} else {
				# �召��������ʂ���
				push(@wd, $decoded_wd);
			}

			# �摜�t�@�C�����������K�\���z��ɒǉ�
			if ($in{'c'} && $decoded_wd =~ /^$img_filename_prefix/) {
				my $word = $decoded_wd;
				$imgfind = 1;
				$word =~ s/^$img_filename_prefix//;
				if ($in{'cs'} eq 'ON') { $word = lc($word); } # �召��������ʂ��Ȃ����߁A�摜�t�@�C�������������ɕϊ�
				if ($word ne '') {
					# �����t�@�C�����𐳋K�\�������̂��߂ɃG�X�P�[�v
					$word = quotemeta($word);
				} else {
					# Prefix�݂̂̎��́A�S�������̐��K�\��
					$word = '.*';
				}
				push(@imgfile_expr, $word);
			}
		}

		my @matched_thread_info_log_array; # ��v�X���b�h���O���z�񃊃t�@�����X�̔z��
		foreach my $logfile (@{$log1[$in{'log'}]}) {
			my $filter_keyname = $logfile eq $nowfile ? "current" : "past";
			open(my $log_fh, "$logfile") || &error("Open Error: $logfile");
			flock($log_fh, 1) || &error("Lock Error: $logfile");
			<$log_fh> if ($logfile eq $nowfile); # �擪�s�X�L�b�v
			while (<$log_fh>) {
				# ���t�w�茟���ŁA���̃X���b�h���O�ł̏o�͑Ώۂ��Ȃ��ꍇ�Ƀ��[�v�E�o
				if($date_filter_hash && keys(%{${$date_filter_hash}{$filter_keyname}}) == 0) { last; }

				chomp($_);

				my $flg = 0; # ��v�X���b�h�t���O
				$target = '';
				my @splitted_thread_info_log_line = split(/<>/, $_);
				$splitted_thread_info_log_line[1] =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
				my ($no,$sub,$res,$nam,$date,$na2,$key,$upl,undef,$restime) = @splitted_thread_info_log_line;

				# ���t�w�茟���ΏۃX���b�h����
				if($date_filter_hash) {
					if(exists(${$date_filter_hash}{$filter_keyname}{$no})) {
						# �o�͑Ώۃn�b�V�����炱�̃X���b�h�ԍ��̃L�[���폜���A�J�E���g����
						delete(${$date_filter_hash}{$filter_keyname}{$no});
					} else {
						# ���t�w��͈͓��̃X���b�h�łȂ���΁A�ǂݔ�΂�
						next;
					}
				}

				# �X���b�h���O�t�@�C���p�X�擾
				my $logfile_path = get_logfolder_path($no) . "/$no.cgi";

				# �L�[���[�h����
				if($in{'type'} eq "keyword") {
					my $filefound_flg = 0;

#					$target .= $sub if ($in{'s'});
#					$target .= $nam if ($in{'n'});

# �����ŋL���̓��e�܂œW�J���āA�����Ώۂɂ���΂����̂��ȁB
#					open(KOBETU,"$logdir/$no\.cgi");
#					$top2 = <KOBETU>;
#					while (<KOBETU>) {
#						(undef,$sub2,undef,undef,$com2,undef) = split(/<>/);
#						$target .= $sub2 if ($in{'r'});
#						$target .= $com2 if ($in{'c'});
#					}
#					close(KOBETU);

# �ʋL���̖{�������̃R�[�h�ȑf���iThanks to MS����j
					if($in{'c'} || $in{'r'}) {
						open(my $thread_log_fh, $logfile_path) || &error("Open Error: $no.cgi");
						flock($thread_log_fh, 1) || &error("Lock Error: $no.cgi");
						<$thread_log_fh>; # �擪�s�X�L�b�v
						while (<$thread_log_fh>){
							$_ =~ s/(?:\r\n|\r|\n)$//;
							my @log = split(/<>/, $_);
							my ($nam2,$com) = @log[2,4];
							$target .= $enc_cp932->decode($com) if ($in{'c'});
							$target .= $enc_cp932->decode($nam2) if ($in{'n'});
							# �摜�t�@�C��������
							if($imgfind) {
								# �A�b�v�摜�t�@�C�������o��
								my ($tim,@upl) = @log[11 .. 14, 23 .. 25];
								my @filenames;
								for (my $i = 0; $i < scalar(@upl); $i++) {
									my $ex = (split(/,/, $upl[$i]))[1];
									if($ex) {
										my $filename = $enc_cp932->decode("$tim-".($i+1)."$ex");
										if($in{'cs'} eq 'ON') { $filename = lc($filename); }
										push(@filenames, $filename);
									}
								}
								# �摜�t�@�C�����������K�\�����X�g��蒆�Ԉ�v����
								for my $expr (@imgfile_expr) {
									my $f = 0;
									for my $filename (@filenames) {
										if($filename =~ /$expr/) {
											$f = 1;
											last;
										}
									}
									if($f) {
										$filefound_flg = 1;
										if($in{"op"} eq "OR") { last; }
									} else {
										if($in{"op"} eq "AND") {
											$filefound_flg = 0;
											last;
										}
									}
								}
							}
							last if (!$in{'r'});
						}
						close($thread_log_fh);
					} else {
						$target .= $enc_cp932->decode($nam) if ($in{'n'});
					}
					$target .= $enc_cp932->decode($sub) if ($in{'s'});

					# �����Ώۂ����ׂď�������
					if ($in{'cs'} eq 'ON' ) { $target = lc($target); }

					# ����
					foreach my $wd (@wd) {
						if (index($target,$wd) >= 0) {
							$flg = 1;
							if ($in{'op'} eq 'OR') { last; }
						} else {
							if ($in{'op'} eq 'AND') { $flg = 0; last; }
						}
					}

					# NOT���� flag���]
					if ($in{'not'}) { $flg = $flg ? 0 : 1; }

					# �摜�t�@�C�����������ʂ�����
					if($imgfind) { $flg = $flg || $filefound_flg; }
				}

				# �o�^ID�����E���[�UID����
				if($in{'type'} eq "user_id" || $in{'type'} eq "patio_id") {
					my %idfound_flgs;
					open(my $thread_log_fh, $logfile_path) || &error("Open Error: $no.cgi");
					flock($thread_log_fh, 1) || &error("Lock Error: $no.cgi");
					<$thread_log_fh>; # �擪�s�X�L�b�v
					THREADLOG_LOOP: while (<$thread_log_fh>){
						chomp($_);
						# �����Ώۂ��o�^ID(16)�����[�UID(15)��������
						$target = $enc_cp932->decode($in{'type'} eq "user_id" ? (split(/<>/))[16] : (split(/<>/))[15]);

						# �����Ώۂ����ׂď�������
						if ($in{'cs'} eq 'ON' ) { $target = lc($target); }

						# ����
						foreach my $wd (@wd) {
							if (index($target,$wd) >= 0) {
								$idfound_flgs{$wd} = 1;
								# �������ʏo�͑Ώ۔���
								if ($in{'op'} eq 'OR' || keys %idfound_flgs == scalar(@wd)) {
									$flg = 1;
									last THREADLOG_LOOP;
								}
							}
						}
					}
					close($thread_log_fh);

					# NOT���� flag���]
					if ($in{'not'}) { $flg = $flg ? 0 : 1; }
				}

				# �Ώۂł���΁A�������ʂƂ��ďo��
				if ($flg) {
					push(@matched_thread_info_log_array, \@splitted_thread_info_log_line);
				}
			}

			close($log_fh);
		}

		# �������ʏo��
		$in{vw} = int($in{vw}); # 1�y�[�W������̕\���X���b�h�����m����int��
		if ($in{vw} < 1) {
			# 1�����̕s���ȃp�����[�^���^����ꂽ���́A1���Ƃ���
			$in{vw} = 1;
		}
		my $match_count = scalar(@matched_thread_info_log_array); # ��v�X���b�h����
		my $page_count = $match_count > 0 ? int(($match_count - 1) / $in{vw}) + 1 : 0; # ���y�[�W��
		my $last_page_index = $match_count > 0 ? ($page_count - 1) * $in{vw} : 0; # $in{vw}�Ŋ���؂�Ȃ��y�[�W����؂�̂ĂāA�ŏI�y�[�W�擪�X���b�h�̃C���f�b�N�X�����肷��
		$p = int(($p / $in{vw}) + 0.5) * $in{vw}; # $p��$in{vw}�Ŋ���؂ꂸ�s���Ȓl�̏ꍇ�ɁA�����_�ȉ����l�̌ܓ����ċ߂��y�[�W�̐擪�X���b�h�C���f�b�N�X�ƂȂ�悤�Čv�Z����
		if ($p < 0) {
			$p = 0; # 0�����̃y�[�W�ԍ��̎��͍ŏ��̃X���b�h�����܂ރy�[�W�Ƃ���
		} elsif ($p > $last_page_index) {
			$p = $last_page_index; # �ŏI�y�[�W���傫�������w�肳�ꂽ���́A�ŏI�y�[�W�Ƃ���
		}
		my $current_page = ($p / $in{vw}) + 1; # ���݃y�[�W

		## ��v�����Etable�^�O�o��
		print <<EOM;
<br>
<h2>��������:${match_count}��</h2>
<br>
<p>
<Table border="0" cellspacing="0" cellpadding="0" id="index_table">
<Tr><Td>
<table id="teeest" border="0" cellspacing="0" cellpadding="5" width="100%">
<tr bgcolor="#bfecbf" class="thth">
  <td bgcolor="#bfecbf">�W�����v</td>
  <td bgcolor="#bfecbf">�X���b�h��</td>
  <td bgcolor="#bfecbf" class="center">��</td>
  <td bgcolor="#bfecbf" class="center">����</td>
EOM

		## tbody�^�O�o��
		print "<tbody bgcolor=\"$col2\"";
		if ($log3[$in{'log'}] eq "cross") {
			# �ꊇ�������́A���s���O�Ɖߋ����O�ŕʂ�ID��t�^����
			print $logfile eq $nowfile ? " id=\"genkoulog\"" : " id=\"kakolog\"";
		}
		print ">\n";

		## ��v�X���b�h���o��
		for (my $i = $p; $i < ($p + $in{vw}) && $i < scalar(@matched_thread_info_log_array); $i++) {
			# �X���b�h���擾
			my ($no, $sub, $res, $nam, $date, $na2, $key, $upl, undef, $restime) = @{$matched_thread_info_log_array[$i]};
			$date =~ s/([0-9][0-9]:[0-9][0-9]):[0-9][0-9].*/\1/g;

			# �A�C�R����`
			if ($key eq '0' || $key eq '4') { $icon = 'fold3.gif'; }
			elsif ($key eq '3') { $icon = 'faq.gif'; }
			elsif ($key == 2) { $icon = 'look.gif'; }
			elsif ($res >= $alarm) { $icon = 'fold5.gif'; }
			elsif (time < $restime + $hot) { $icon = 'foldnew.gif'; }
			elsif ($upl) { $icon = 'fold6.gif'; }
			else { $icon = 'fold1.gif'; }

			print "<tr bgcolor=\"$col2\">";

			print "<td width=\"30\">";
			print "<p class=\"thread\"><a href=\"$readcgi?no=$no$num#$res3\">>></a></p>";
			print "</td>";

			print "<td bgcolor=\"$col2\" class=\"test5\">";
			print "<a href=\"$readcgi?no=$no\">$sub</a></td>";
			print "<td align=\"center\" width=\"70px\">$res</td>";

			print "<td align=\"center\" width=\"150px\">$date</td>";
			print "</tr>\n";
		}

		## tbody���^�O�o��
		print "</tbody>\n";

		## table���^�O�o��
		print "</table></Td></Tr></Table>\n";

		## �y�[�W�ړ������N (�����y�[�W�\���ɂȂ鎞�̂ݏo��)
		if ($page_count > 1) {
			print "<br><table style=\"width: 100%\">\n";

			# ���ݕ\���y�[�W/�S�y�[�W���\��
			print "<tr><td class=\"num\" align=\"center\">$current_page/$page_count</td></tr>\n";

			# 1�y�[�W�ځE�O��y�[�W�E�ŏI�y�[�W�ւ̃����N
			print "<tr><td class=\"num\" align=\"center\">";
			if ($p <= 0) {
				print "&lt;&lt;�@�O�ց@";
			} else {
				my $prev_page_index = $p - $in{vw}; # �O�y�[�W�̐擪�X���b�h�C���f�b�N�X
				if ($prev_page_index < 0) {
					# �O�y�[�W�̈ꕔ�̃X���b�h���擪�y�[�W�ɂ�����Ƃ��́A�ŏI�y�[�W�̐擪�X���b�h�C���f�b�N�X�Ƃ���
					$prev_page_index = 0;
				}
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val(0); \$('form').submit(); return false;\">&lt;&lt;</a>�@";
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($prev_page_index); \$('form').submit(); return false;\">�O��</a>�@";
			}
			if ($p >= $last_page_index) {
				print "���ց@&gt;&gt;";
			} else {
				my $next_page_index = $p + $in{vw}; # ���y�[�W�̐擪�X���b�h�C���f�b�N�X
				if ($next_page_index > $last_page_index) {
					# ���y�[�W�̈ꕔ�̃X���b�h���ŏI�y�[�W�ɂ�����Ƃ��́A1�y�[�W�ڂ̐擪�X���b�h�C���f�b�N�X�Ƃ���
					$next_page_index = $last_page_index;
				}
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($next_page_index); \$('form').submit(); return false;\">����</a>�@";
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($last_page_index); \$('form').submit(); return false;\">&gt;&gt;</a>";

			}
			print "</td></tr>\n";

			print "</table>\n";
		}
	}
	print "</div>\n</body></html>\n";
	exit;
}

# �Z�b�V����Cookie�Ɍ��������ƌ����������Z�b�g
sub set_find_cookie {
	my ($set_hash_data) = @_;

	# Cookie�f�[�^���쐬
	my $cookie_data;
	if (scalar(keys(%{$set_hash_data})) > 0) {
		$cookie_data = $json_webencryption_instance->encode_from_hash($set_hash_data);
		if (length($cookie_data) > 4093) {
			# �ő�i�[�T�C�Y���߂̂��߁A�G���[�I��
			return 0;
		}
	}

	# Cookie�Z�b�g
	print "Set-Cookie: $find_cookie_name=$cookie_data;\n";
	return 1;
}

# �Z�b�V����Cookie����ߋ��̌��������ƌ���������ǂݎ��
sub read_find_cookie {
	my $find_cookie;
	foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
		my ($key, $value) = split(/=/, $cookie_set);
		if ($key eq $find_cookie_name) {
			if ($value ne '') {
				$find_cookie = $json_webencryption_instance->decode_to_hash($value);
			}
			last;
		}
	}
	return defined($find_cookie) ? $find_cookie : {};
}

1;
