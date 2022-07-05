#┌─────────────────────────────────
#│ [ WebPatio ]
#│ find.pl - 2007/04/09
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# 2011/07/29 コメントアウトのバグ修正
# 2011/04/27 大小同一視のバグ修正
# 2010/10/19 本文検索の簡素化コードを取り込み
# 2010/01/11 トピックスか名前をチェックしないと検索が実行されないのを修正
# 2009/12/07 ページ送りのリンクにオプションが反映されていなかった
# 2009/07/02 記録内容にスタート、件数を追加
# 2009/06/01 FAQモードの表示に対応
# 2007/05/10 本文も検索対象に

#-------------------------------------------------
#  ワード検索
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
	# セッションCookie名定義
	$find_cookie_name = "WEB_PATIO_${cookie_current_dirpath}_FIND_LIST";

	# JSON::WebEncryption インスタンス作成
	$json_webencryption_instance = JSON::WebEncryption->new(
		'alg'         => 'RSA1_5',
		'enc'         => 'A256CBC-HS512',
		'private_key' => $find_recaptcha_continue_cookie_rsa_private_key,
		'public_key'  => $find_recaptcha_continue_cookie_rsa_public_key
	);
}

sub find {
	local($target,$alarm,$next,$back,$enwd,$imgfind,@log1,@log2,@log3,@wd,@imgfile_expr,@findtypes,$find_log_append_contents);

	# 検索種別定義
	@findtypes = (["キーワード検索", "keyword"], ["登録ID検索", "user_id"], ["ユーザID検索", "patio_id"]);

	# 検索を実行するかどうか
	my $performFinding = $in{'word'} && ($in{'type'} eq "keyword" && $in{'s'} || $in{'n'} || $in{'r'} || $in{'c'}) || $in{'type'} eq "user_id" || $in{'type'} eq "patio_id";

	# GETメソッドによるアクセス時
	if (!$postflag) {
		if ($performFinding) {
			# GETメソッドで検索を実行した場合は、URLクリアのため301リダイレクト
			print "Status: 301 Moved Permanently\n";
			print "Location: " . URI->new("$bbscgi?mode=find")->abs($ENV{'REQUEST_URI'}) . "\n\n";
			exit(0);
		} else {
			# GETメソッドで、不正な検索フォーム値を受け取らないために初期化
			undef(%in);
			$in{'mode'} = 'find';
		}
	}

	# 検索実行時はページ間移動ではない検索かどうか
	my $is_first_find = $performFinding && $in{'p'} eq '';

	# 検索キーワード最適化・検索ログ書き込み文字列作成
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

	# reCAPTCHA認証
	my $display_recaptcha_form = 0;
	if ($find_recaptcha || $in{'g-recaptcha-response'} ne '') {
		my $find_cookie;
		if ($find_recaptcha_continue) {
			# セッションCookieから過去の検索語/タイムスタンプを読み取り
			$find_cookie = read_find_cookie();
			foreach my $word (keys(%{$find_cookie})) {
				# 同一条件連続検索数カウント時間を過ぎたタイムスタンプを自動消去
				@{${$find_cookie}{$word}} = grep { $_ + $find_recaptcha_continue_count_time > $time } @{${$find_cookie}{$word}};
			}
		}

		# reCAPTCHA認証表示判定
		my ($perform_recaptcha_auth, $find_log_fh, $auth_host_log_fh);
		if (!$performFinding) {
			# 検索フォームのみ表示時
			if (open($find_log_fh, '<', $find_recaptcha_count_log) && flock($find_log_fh, 1) # 消去検索ログオープン
				&& open($auth_host_log_fh, '+>>', $find_recaptcha_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA認証対象ホストログオープン
				# 消去検索ログ行数カウント
				my $find_count = 0;
				while (sysread $find_log_fh, my $buffer, 4096) {
					$find_count += ($buffer =~ tr/\n//);
				}
				$find_count--; # 先頭行分を差し引き
				$display_recaptcha_form = $find_count + 1 > $find_recaptcha_permit; # 連続検索許容数を超えて検索しようとしているため、reCAPTCHA認証を有効
				close($find_log_fh);

				# reCAPTCHA認証対象ホストログで
				# ホストが一致する場合は更新、それ以外でも認証対象の場合は追記する
				my $auth_host_log = "日時,検索語,ホスト,タイムスタンプ\n";
				<$auth_host_log_fh>; # 先頭行読み飛ばし
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
			# 検索実行時
			if (open($find_log_fh, '+>>', $find_recaptcha_count_log) && flock($find_log_fh, 2) && seek($find_log_fh, 0, 0) # 消去検索ログオープン
				&& open($auth_host_log_fh, '+>>', $find_recaptcha_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) { # reCAPTCHA認証対象ホストログオープン
				# reCAPTCHAレスポンスが送信されてきた時は、設定にかかわらず認証を実施
				$perform_recaptcha_auth = $in{'g-recaptcha-response'} ne '';

				# 消去検索ログ行数カウント・消去対象行除外
				my $find_log = "日時,検索語,表\示件数,ホスト,検索種別,タイムスタンプ\n";
				my $find_count = 0;
				my $delete_time_not_reached_find_count = 0;
				my $is_find_log_changed = 0;
				my $is_recaptcha_enabled_in_delete_log = 0;
				<$find_log_fh>; # 先頭行読み飛ばし
				while (<$find_log_fh>) {
					chomp($_);
					my @line = split(/,/, $_);
					if (scalar(@line) == 6) {
						# 自動消去が無効か、消去時間が経過していないログのみ残す
						if ($find_recaptcha_count_time == 0 || ($line[5] + $find_recaptcha_count_time >= $time)) {
							$find_log .= "$_\n";
							$delete_time_not_reached_find_count++;
						} else {
							$is_find_log_changed = 1;
						}
						$find_count++; # カウントは別に行う
					}
				}
				if ($. < 1) {
					$is_find_log_changed = 1;
				}
				$is_recaptcha_enabled_in_delete_log = $find_count + 1 > $find_recaptcha_permit; # 連続検索許容数を超えて検索しようとしている、reCAPTCHA認証対象かどうか
				$perform_recaptcha_auth ||= $is_recaptcha_enabled_in_delete_log;
				$display_recaptcha_form ||= $delete_time_not_reached_find_count + 1 > $find_recaptcha_permit; # 検索実行後の連続検索数が許容数を超えて、reCAPTCHA表示対象かどうか

				# reCAPTCHA認証対象ホストログ確認
				my $auth_host_log = "日時,検索語,ホスト,タイムスタンプ\n";
				my $host_found_in_recaptcha_auth_log = 0;
				my $is_auth_host_log_changed = 0;
				<$auth_host_log_fh>; # 先頭行読み飛ばし
				while (<$auth_host_log_fh>) {
					chomp($_);
					my @line = split(/,/, $_);
					if (scalar(@line) == 4) {
						# 同一ホストが見つかった時、認証対象とする
						my $is_current_line_same_host = $line[2] eq $host;
						if ($is_current_line_same_host) {
							$perform_recaptcha_auth = 1;
							$host_found_in_recaptcha_auth_log = 1;
						}
						# 自動消去が無効か、消去時間が経過していないログのみ残す
						if ($find_recaptcha_auth_host_release_time == 0 || ($line[3] + $find_recaptcha_auth_host_release_time >= $time)) {
							if ($is_current_line_same_host) {
								$display_recaptcha_form = 1; # 同一ホストが見つかった時、消去時間が経過していなければreCAPTCHAを再表示
								$is_auth_host_log_changed = 1;
							} else {
								$auth_host_log .= "$_\n";
							}
						} else {
							$is_auth_host_log_changed = 1;
						}
					}
				}
				# reCAPTCHA認証対象になったホストをログに追加
				if ($. < 1 || $display_recaptcha_form || ($is_recaptcha_enabled_in_delete_log && !$host_found_in_recaptcha_auth_log)) {
					if ($display_recaptcha_form || ($is_recaptcha_enabled_in_delete_log && !$host_found_in_recaptcha_auth_log)) {
						$auth_host_log .= "$date,$in{'word'},$host,$time\n";
					}
					$is_auth_host_log_changed = 1;
				}

				my $utf8flagged_find_word;
				if ($find_recaptcha_continue) {
					# 同一条件でのページ遷移による検索実行時のreCAPTCHA認証スキップ判定
					$utf8flagged_find_word = $enc_cp932->decode($in{'word'});
					my $skip_recaptcha_auth_by_page_moving = 0;
					if (!$is_first_find && exists(${$find_cookie}{$utf8flagged_find_word})) {
						$skip_recaptcha_auth_by_page_moving = scalar(@{${$find_cookie}{$utf8flagged_find_word}}) + 1 > $find_recaptcha_continue_permit;
						$perform_recaptcha_auth &&= $skip_recaptcha_auth_by_page_moving;
					}
				}

				# reCAPTCHA認証実施
				if ($perform_recaptcha_auth) {
					# reCAPTCHAが表示されないか、チェックを行っていない時など
					# reCAPTCHAレスポンスが送信されてきていない時は、APIとの通信を行わない
					my $is_recaptcha_auth_success = 0;
					if ($in{'g-recaptcha-response'} ne '') {
						# reCAPCTHA APIと通信
						my $lwp_ua = LWP::UserAgent->new(timeout => 2);
						my $lwp_response = $lwp_ua->post(
							'https://www.google.com/recaptcha/api/siteverify',
							[ secret => $recaptcha_secret_key, response => $in{'g-recaptcha-response'} ]
						);

						if ($lwp_response->is_success) {
							# 正常に通信を行えた場合にのみ認証状況の確認を行う
							my $result = JSON::XS->new()->decode($lwp_response->content);
							my $is_bool = $JSON::XS::VERSION >= 3 ? \&Types::Serialiser::is_bool : \&JSON::XS::is_bool;
							if (${$result}{'success'} && $is_bool->(${$result}{'success'})) {
								# 認証成功
								$is_recaptcha_auth_success = 1;
							}
						} else {
							# 通信失敗時は認証成功したものとみなす
							$is_recaptcha_auth_success = 1;
						}
					}

					# 認証失敗時はエラー表示
					if (!$is_recaptcha_auth_success) {
						if (!exists($in{'g-recaptcha-response'})) {
							# reCAPTCHAレスポンスフィールドが無い場合は、検索ページにリンク
							error("前画面に戻り、ページを再読み込みして認証を行って下さい。", "$bbscgi?mode=find");
						} else {
							# reCAPTCHAが表示されているページだった場合はブラウザヒストリーで戻る
							my $msg = "認証に失敗しているか、有効期限が切れています。";
							if ($skip_recaptcha_auth_by_page_moving) {
								$msg .= "引き続きページ移動を行う場合は、認証を行った後ページ移動をして下さい。";
							}
							error($msg);
						}
					}
				}

				# 消去検索ログへ書き込み
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

				# reCAPTCHA認証対象ホストログへ書き込み
				if ($is_auth_host_log_changed) {
					seek($auth_host_log_fh, 0, 0);
					truncate($auth_host_log_fh, 0);
					print $auth_host_log_fh $auth_host_log;
				}
				close($auth_host_log_fh);

				# 検索実行時に、セッションCookie内容変数に検索語/タイムスタンプを追加
				if ($find_recaptcha_continue) {
					push(@{${$find_cookie}{$utf8flagged_find_word}}, $time);
				}
			} else {
				error("Error: reCAPTCHA");
			}
		}

		if ($find_recaptcha_continue) {
			# セッションCookie格納ハッシュからタイムスタンプが1つもない検索語を削除
			foreach my $word (keys(%{$find_cookie})) {
				if (scalar(@{${$find_cookie}{$word}}) == 0) {
					delete(${$find_cookie}{$word});
				}
			}
			# セッションCookieに保存
			# 最大格納サイズを超えているときは、
			# 最後の検索時刻が最も古い検索語を捨てる
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

	# 累積検索ログ書き込み
	if ($performFinding && $srchlog) {
		my $srchlog_fh;
		(open($srchlog_fh, '+>>', $srchlog) && flock($srchlog_fh, 2) && seek($srchlog_fh, 0, 0)) || error("Write Error: $srchlog");
		<$srchlog_fh>;
		if ($. < 1) {
			seek($srchlog_fh, 0, 0);
			truncate($srchlog_fh, 0);
			print $srchlog_fh "日時,検索語,表\示件数,ホスト,検索種別,タイムスタンプ\n";
		} elsif ($is_first_find) {
			seek($srchlog_fh, 0, 2);
		}
		if ($is_first_find) {
			print $srchlog_fh $find_log_append_contents;
		}
		close($srchlog_fh);
	}

	# フォーム初期値や検索で使用する日付文字列を予めフォーマットする
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
tr.test1 a,	/* 管理者ロック */
tr.test3 a,	/* 	スレッド落ち寸前マーク */
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
<a href="$bbscgi?">トップページ</a> &gt; ワード検索
</td></tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/glass.gif" align="middle">
&nbsp;<b>ワード検索</b></td>
</tr></table></Td></Tr></Table>
<P>
<form action="$bbscgi?mode=find" method="post">
<input type="hidden" name="mode" value="find">
<input type="hidden" name="p" value="">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2"><td bgcolor="$col2">
キーワード <input type="text" name="word" size="38" value="$in{'word'}"> &nbsp;
条件 <select name="op">
EOM

	foreach ("AND", "OR") {
		print "<option";
		if ($in{'op'} eq $_) {
			print " selected";
		}
		print ">$_</option>\n";
	}
	print "</select> &nbsp; NOT検索 ";
	if($in{'not'}) {
		print "<input type=checkbox name=\"not\" value=\"1\" checked>";
	} else {
		print "<input type=checkbox name=\"not\" value=\"1\">";
	}
	print " &nbsp; 表\示 <select name=vw>\n";
	foreach (1,2,3,5,7,9,10,100,150,200,250) {
		if ($in{'vw'} == $_) {
			print "<option value=\"$_\" selected>$_件\n";
		} else {
			print "<option value=\"$_\">$_件\n";
		}
	}
	print "</select> 大文字小文字を区別しない <select name=cs>\n";
	foreach ("ON", "OFF") {
		if ($in{'cs'} eq $_) {
			print "<option value=\"$_\" selected>$_\n";
		} else {
			print "<option value=\"$_\">$_\n";
		}
	}
	print "</select><br>";

	print "<br>期間指定(最終書込時間) ";
	print "<input type=date name=\"dateFrom\" value=\"$in{'dateFrom'}\"> ～ <input type=date name=\"dateTo\" value=\"$in{'dateTo'}\">";

	print "<br>検索範囲 ";
	if ($in{'log'} eq "") { $in{'log'} = 2; }
	@log1 = ([$nowfile], [$pastfile], [$nowfile, $pastfile]);
	@log2 = ("現行ログ", "過去ログ", "一括検索");
	@log3 = ("view", "past", "cross");
	foreach (0..$#log2) {
		if ($in{'log'} == $_) {
			print "<input type=radio name=log value=\"$_\" checked>$log2[$_]\n";
		} else {
			print "<input type=radio name=log value=\"$_\">$log2[$_]\n";
		}
	}

	print "<br>検索種別 ";
	if($in{'type'} ne "keyword" && $in{'type'} ne "user_id" && $in{'type'} ne "patio_id") {
		$in{'type'} = "keyword";
	}
	for(my $i=0; $i<scalar(@findtypes); $i++) {
		print "<input type=\"radio\" name=\"type\" value=\"${$findtypes[$i]}[1]\"";
		if(${$findtypes[$i]}[1] eq $in{'type'}) { print " checked=\"checked\""; }
		print ">${$findtypes[$i]}[0]";
	}

	print "<span id=\"findItem\"><br>検索項目 ";
	if ($in{'s'} eq "" && $in{'word'} eq "") { $in{'s'} = 1; }
	if ($in{'s'} == 1) {
		print "<input type=checkbox name=s value=\"1\" checked>トピックス\n";
	} else {
		print "<input type=checkbox name=s value=\"1\">トピックス\n";
	}
	if ($in{'n'} eq "" && $in{'word'} eq "") { $in{'n'} = 0; }
	if ($in{'n'} == 1) {
		print "<input type=checkbox name=n value=\"1\" checked>名前\n";
	} else {
		print "<input type=checkbox name=n value=\"1\">名前\n";
	}
	if ($in{'r'} eq "" && $in{'word'} eq "") { $in{'r'} = 1; }
	if ($in{'r'} == 1) {
		print "<input type=checkbox name=r value=\"1\" checked>レスのタイトル\n";
	} else {
		print "<input type=checkbox name=r value=\"1\">レスのタイトル\n";
	}

	if ($in{'c'} eq "" && $in{'word'} eq "") { $in{'c'} = 1; }
	if ($in{'c'} == 1) {
		print "<input type=checkbox name=c value=\"1\" checked>本文\n";
	} else {
		print "<input type=checkbox name=c value=\"1\">本文\n";
	}
	print "</span>";

	print <<EOM;
&nbsp;&nbsp;
<input type="submit" value="検索実行" onclick=\"\$('input[name=p]').val(''); return true;\">
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

	# 検索実行
	if ($performFinding) {

		# アラーム数定義
		$alarm = int($m_max*0.9);

		# 日付検索範囲をパース
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
			# 時間的にdate_fromよりdate_toが前の場合に入れ替える
			($date_from, $date_to) = ($date_to, $date_from);
		}
		if(defined($date_to)) {
			# date_toはその日の23:59:59までを対象とする
			$date_to = $date_to + ONE_DAY - 1;
		}

		# 日付範囲が定義されていれば範囲検索を行う
		my $date_filter_hash = undef;
		if(defined($date_from) || defined($date_to)) {
			my $current_log_flg = $in{'log'} ne "1" ? 1 : 0;
			my $past_log_flg = $in{'log'} ne "0" ? 1 : 0;

			# スレッド更新日時管理データベースに接続して範囲検索
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$date_filter_hash = $updatelog_db->find_threads_by_period($date_from, $date_to, $i_max * $current_log_flg, $p_max * $past_log_flg);
			$updatelog_db->close(0);
		}

		# フォーム用に検索キーワードを退避
		$enwd = &url_enc($in{'word'});

		# 検索キーワードを半角スペースで分割
		foreach my $encoded_wd (split(/\s+/, $in{'word'})) {
			# 内部エンコードに変換
			my $decoded_wd = $enc_cp932->decode($encoded_wd);

			# 検索キーワード配列に追加
			if ($in{'cs'} eq 'ON') {
				# 大小文字を区別しないため、検索語を小文字に変換
				push(@wd, lc($decoded_wd));
			} else {
				# 大小文字を区別する
				push(@wd, $decoded_wd);
			}

			# 画像ファイル名検索正規表現配列に追加
			if ($in{'c'} && $decoded_wd =~ /^$img_filename_prefix/) {
				my $word = $decoded_wd;
				$imgfind = 1;
				$word =~ s/^$img_filename_prefix//;
				if ($in{'cs'} eq 'ON') { $word = lc($word); } # 大小文字を区別しないため、画像ファイル名を小文字に変換
				if ($word ne '') {
					# 検索ファイル名を正規表現検索のためにエスケープ
					$word = quotemeta($word);
				} else {
					# Prefixのみの時は、全件検索の正規表現
					$word = '.*';
				}
				push(@imgfile_expr, $word);
			}
		}

		my @matched_thread_info_log_array; # 一致スレッドログ情報配列リファレンスの配列
		foreach my $logfile (@{$log1[$in{'log'}]}) {
			my $filter_keyname = $logfile eq $nowfile ? "current" : "past";
			open(my $log_fh, "$logfile") || &error("Open Error: $logfile");
			flock($log_fh, 1) || &error("Lock Error: $logfile");
			<$log_fh> if ($logfile eq $nowfile); # 先頭行スキップ
			while (<$log_fh>) {
				# 日付指定検索で、このスレッドログでの出力対象がない場合にループ脱出
				if($date_filter_hash && keys(%{${$date_filter_hash}{$filter_keyname}}) == 0) { last; }

				chomp($_);

				my $flg = 0; # 一致スレッドフラグ
				$target = '';
				my @splitted_thread_info_log_line = split(/<>/, $_);
				$splitted_thread_info_log_line[1] =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
				my ($no,$sub,$res,$nam,$date,$na2,$key,$upl,undef,$restime) = @splitted_thread_info_log_line;

				# 日付指定検索対象スレッド判定
				if($date_filter_hash) {
					if(exists(${$date_filter_hash}{$filter_keyname}{$no})) {
						# 出力対象ハッシュからこのスレッド番号のキーを削除し、カウントする
						delete(${$date_filter_hash}{$filter_keyname}{$no});
					} else {
						# 日付指定範囲内のスレッドでなければ、読み飛ばし
						next;
					}
				}

				# スレッドログファイルパス取得
				my $logfile_path = get_logfolder_path($no) . "/$no.cgi";

				# キーワード検索
				if($in{'type'} eq "keyword") {
					my $filefound_flg = 0;

#					$target .= $sub if ($in{'s'});
#					$target .= $nam if ($in{'n'});

# ここで記事の内容まで展開して、検索対象にすればいいのかな。
#					open(KOBETU,"$logdir/$no\.cgi");
#					$top2 = <KOBETU>;
#					while (<KOBETU>) {
#						(undef,$sub2,undef,undef,$com2,undef) = split(/<>/);
#						$target .= $sub2 if ($in{'r'});
#						$target .= $com2 if ($in{'c'});
#					}
#					close(KOBETU);

# 個別記事の本文検索のコード簡素化（Thanks to MSさん）
					if($in{'c'} || $in{'r'}) {
						open(my $thread_log_fh, $logfile_path) || &error("Open Error: $no.cgi");
						flock($thread_log_fh, 1) || &error("Lock Error: $no.cgi");
						<$thread_log_fh>; # 先頭行スキップ
						while (<$thread_log_fh>){
							$_ =~ s/(?:\r\n|\r|\n)$//;
							my @log = split(/<>/, $_);
							my ($nam2,$com) = @log[2,4];
							$target .= $enc_cp932->decode($com) if ($in{'c'});
							$target .= $enc_cp932->decode($nam2) if ($in{'n'});
							# 画像ファイル名検索
							if($imgfind) {
								# アップ画像ファイル情報取り出し
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
								# 画像ファイル名検索正規表現リストより中間一致検索
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

					# 検索対象をすべて小文字に
					if ($in{'cs'} eq 'ON' ) { $target = lc($target); }

					# 検索
					foreach my $wd (@wd) {
						if (index($target,$wd) >= 0) {
							$flg = 1;
							if ($in{'op'} eq 'OR') { last; }
						} else {
							if ($in{'op'} eq 'AND') { $flg = 0; last; }
						}
					}

					# NOT検索 flag反転
					if ($in{'not'}) { $flg = $flg ? 0 : 1; }

					# 画像ファイル名検索結果を結合
					if($imgfind) { $flg = $flg || $filefound_flg; }
				}

				# 登録ID検索・ユーザID検索
				if($in{'type'} eq "user_id" || $in{'type'} eq "patio_id") {
					my %idfound_flgs;
					open(my $thread_log_fh, $logfile_path) || &error("Open Error: $no.cgi");
					flock($thread_log_fh, 1) || &error("Lock Error: $no.cgi");
					<$thread_log_fh>; # 先頭行スキップ
					THREADLOG_LOOP: while (<$thread_log_fh>){
						chomp($_);
						# 検索対象が登録ID(16)かユーザID(15)かを決定
						$target = $enc_cp932->decode($in{'type'} eq "user_id" ? (split(/<>/))[16] : (split(/<>/))[15]);

						# 検索対象をすべて小文字に
						if ($in{'cs'} eq 'ON' ) { $target = lc($target); }

						# 検索
						foreach my $wd (@wd) {
							if (index($target,$wd) >= 0) {
								$idfound_flgs{$wd} = 1;
								# 検索結果出力対象判定
								if ($in{'op'} eq 'OR' || keys %idfound_flgs == scalar(@wd)) {
									$flg = 1;
									last THREADLOG_LOOP;
								}
							}
						}
					}
					close($thread_log_fh);

					# NOT検索 flag反転
					if ($in{'not'}) { $flg = $flg ? 0 : 1; }
				}

				# 対象であれば、検索結果として出力
				if ($flg) {
					push(@matched_thread_info_log_array, \@splitted_thread_info_log_line);
				}
			}

			close($log_fh);
		}

		# 検索結果出力
		$in{vw} = int($in{vw}); # 1ページあたりの表示スレッド数を確実にintに
		if ($in{vw} < 1) {
			# 1未満の不正なパラメータが与えられた時は、1件とする
			$in{vw} = 1;
		}
		my $match_count = scalar(@matched_thread_info_log_array); # 一致スレッド件数
		my $page_count = $match_count > 0 ? int(($match_count - 1) / $in{vw}) + 1 : 0; # 総ページ数
		my $last_page_index = $match_count > 0 ? ($page_count - 1) * $in{vw} : 0; # $in{vw}で割り切れないページ数を切り捨てて、最終ページ先頭スレッドのインデックスを決定する
		$p = int(($p / $in{vw}) + 0.5) * $in{vw}; # $pが$in{vw}で割り切れず不正な値の場合に、小数点以下を四捨五入して近いページの先頭スレッドインデックスとなるよう再計算する
		if ($p < 0) {
			$p = 0; # 0未満のページ番号の時は最初のスレッド情報を含むページとする
		} elsif ($p > $last_page_index) {
			$p = $last_page_index; # 最終ページより大きい数が指定された時は、最終ページとする
		}
		my $current_page = ($p / $in{vw}) + 1; # 現在ページ

		## 一致件数・tableタグ出力
		print <<EOM;
<br>
<h2>検索結果:${match_count}件</h2>
<br>
<p>
<Table border="0" cellspacing="0" cellpadding="0" id="index_table">
<Tr><Td>
<table id="teeest" border="0" cellspacing="0" cellpadding="5" width="100%">
<tr bgcolor="#bfecbf" class="thth">
  <td bgcolor="#bfecbf">ジャンプ</td>
  <td bgcolor="#bfecbf">スレッド名</td>
  <td bgcolor="#bfecbf" class="center">数</td>
  <td bgcolor="#bfecbf" class="center">時間</td>
EOM

		## tbodyタグ出力
		print "<tbody bgcolor=\"$col2\"";
		if ($log3[$in{'log'}] eq "cross") {
			# 一括検索時は、現行ログと過去ログで別のIDを付与する
			print $logfile eq $nowfile ? " id=\"genkoulog\"" : " id=\"kakolog\"";
		}
		print ">\n";

		## 一致スレッド情報出力
		for (my $i = $p; $i < ($p + $in{vw}) && $i < scalar(@matched_thread_info_log_array); $i++) {
			# スレッド情報取得
			my ($no, $sub, $res, $nam, $date, $na2, $key, $upl, undef, $restime) = @{$matched_thread_info_log_array[$i]};
			$date =~ s/([0-9][0-9]:[0-9][0-9]):[0-9][0-9].*/\1/g;

			# アイコン定義
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

		## tbody閉じタグ出力
		print "</tbody>\n";

		## table閉じタグ出力
		print "</table></Td></Tr></Table>\n";

		## ページ移動リンク (複数ページ表示になる時のみ出力)
		if ($page_count > 1) {
			print "<br><table style=\"width: 100%\">\n";

			# 現在表示ページ/全ページ数表示
			print "<tr><td class=\"num\" align=\"center\">$current_page/$page_count</td></tr>\n";

			# 1ページ目・前後ページ・最終ページへのリンク
			print "<tr><td class=\"num\" align=\"center\">";
			if ($p <= 0) {
				print "&lt;&lt;　前へ　";
			} else {
				my $prev_page_index = $p - $in{vw}; # 前ページの先頭スレッドインデックス
				if ($prev_page_index < 0) {
					# 前ページの一部のスレッドが先頭ページにかかるときは、最終ページの先頭スレッドインデックスとする
					$prev_page_index = 0;
				}
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val(0); \$('form').submit(); return false;\">&lt;&lt;</a>　";
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($prev_page_index); \$('form').submit(); return false;\">前へ</a>　";
			}
			if ($p >= $last_page_index) {
				print "次へ　&gt;&gt;";
			} else {
				my $next_page_index = $p + $in{vw}; # 次ページの先頭スレッドインデックス
				if ($next_page_index > $last_page_index) {
					# 次ページの一部のスレッドが最終ページにかかるときは、1ページ目の先頭スレッドインデックスとする
					$next_page_index = $last_page_index;
				}
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($next_page_index); \$('form').submit(); return false;\">次へ</a>　";
				print "<a href=\"#\" onclick=\"\$('input[name=p]').val($last_page_index); \$('form').submit(); return false;\">&gt;&gt;</a>";

			}
			print "</td></tr>\n";

			print "</table>\n";
		}
	}
	print "</div>\n</body></html>\n";
	exit;
}

# セッションCookieに検索条件と検索時刻をセット
sub set_find_cookie {
	my ($set_hash_data) = @_;

	# Cookieデータを作成
	my $cookie_data;
	if (scalar(keys(%{$set_hash_data})) > 0) {
		$cookie_data = $json_webencryption_instance->encode_from_hash($set_hash_data);
		if (length($cookie_data) > 4093) {
			# 最大格納サイズ超過のため、エラー終了
			return 0;
		}
	}

	# Cookieセット
	print "Set-Cookie: $find_cookie_name=$cookie_data;\n";
	return 1;
}

# セッションCookieから過去の検索条件と検索時刻を読み取り
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
