#!/usr/bin/perl

#┌─────────────────────────────────
#│ [ WebPatio ]
#│ patio.cgi - 2007/06/06
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# きりしま式 K0.98
# 2010/11/14 スレ番号の表示をオプションで選べるように
# 2010/10/19 auro_link で >> の処理が無効になったままだったので修正
# 2009/12/06 auto_link の置換文字列に間違い。
# 2009/07/01 過去ログで明示的に &mode=past なのにフラグが立っていないと現行ログとして処理しているのを修正
# 2009/07/01 $restitle=1のとき、スレをソートするチェックボックスが出ていなかった
# 2009/07/01 リンクのrel=nofollowを自サイト内のみ削除するように
# 2009/06/23 $restitleを1にすることでプレビュー機能を無効に出来るように修正（Thanks to 軌道様）
# 2009/06/21 $t_maxと$resが同じになると記事が表示されない現象への対処の見直し
# 2009/06/21 個別記事表示のアイコンが変化するように、またリンク先を元のスレに。$t_maxと$resが同じになると記事が表示されない現象にとりあえず対処（あってるかな）
# 2009/06/19 レスのデフォルトタイトルを有効にしていても反映されない
# 2009/06/16 ファイルのアップロードができないので、プレビュー時に指定することに修正
# 2009/06/15 レス番号がおかしくなるバグ修正
# 2009/06/02 レスにもタイトル設定機能
# 2009/06/02 レスができなくなっているバグの修正
# 2009/06/01 ユーザー間メール機能を無効にできるように、タイトルを後から入力できるように
# 2009/04/07 過去ログの呼び方で現行ログを表示すると過去ログのように表示されるのを抑制する機能のテスト
# 2009/03/28 総合モード
# 2009/03/25 rel=nofollowの記述ミス、記述漏れを修正
# 2009/03/14 新規スレッド作成制限モードの追加・外部へのリンクに nofollow 追加。
# 2008/10/17 レス指定表示のバグ修正
# 2008/08/29 いったん一式アーカイブを更新
# 2008/04/15 メール送信フォームへのリンクのバグ修正
# 2008/01/09 過去ログのフラグになっているスレは、viewで呼び出しても過去ログとして表示
# 2007/10/27 レスのレスを全て表示に取り組み
# 2007/06/10 3.2相当に修正
#----------------------------------
#メモ欄
# $dat 投稿日時
#----------------------------------
BEGIN {
	# 外部ファイル取り込み
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

# Matcher::Utils インスタンス初期化
# (内部で Matcher::Variable インスタンスを初期化してセット)
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

# CookieAのインスタンスを初期化し、CookieAの値と現時点での発行状況を取得 (発行はしない)
my $cookie_a_instance = UniqueCookie->new($cookie_current_dirpath);
my ($cookie_a, $is_cookie_a_issued) = ($cookie_a_instance->value(), $cookie_a_instance->is_issued());

# Cookieに保存されている登録IDを取得
my $cuser_id = do {
	my @cookies = get_cookie();
	$cookies[5] || '';
};

# 書込IDを取得
my $chistory_id = do {
	my $instance = HistoryCookie->new();
	$instance->get_history_id();
};

# 初回Cookieインスタンス初期化
my $first_cookie = FirstCookie->new(
	$mu,
	$firstpost_restrict_settings_filepath,
	$time, $host, $useragent, $cookie_a_instance, $cuser_id, $chistory_id, 0,
	$cookie_current_dirpath, \@firstpost_restrict_exempt
);

# 新規スレッド作成/投稿プレビューでは、初回書き込みまでの時間制限機能の判定を行う
if ($mode eq "form" || $mode eq "resview" || $mode eq "preview") {
	$first_cookie->judge_and_update_cookie(FirstCookie::THREAD_CREATE, undef);
}

# 自分の投稿を目立たせる機能 有効状態取得
my $highlight_name_in_own_post = get_highlight_name_on_own_post();

# ユーザ強調表示機能 色名・カラーコード定義
my @highlight_userinfo_color_name_code = (
    ['赤', '#ff7f50'], ['緑', '#bfecbf'], ['オレンジ', '#ffa500'], ['青', '#87cefa'], ['紫', '#ca95ff'],
    ['ピンク', '#ffb6c1'], ['黄茶', '#bdb76b'], ['黄緑', '#e0f800'], ['赤茶', '#850000'], ['濃緑', '#228b22']
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

# 表示内容分岐機能の分岐判定で使用します
my @decoded_contents_branching_keyword = do {
	my @tmp_decoded_array;
	foreach my $encoded_keyword (@contents_branching_keyword) {
		push(@tmp_decoded_array, $enc_cp932->decode($encoded_keyword)); # 対象文字列を内部エンコードに変換
	}
	(@tmp_decoded_array);
};

&view;

#-------------------------------------------------
#  スレ閲覧
#-------------------------------------------------
sub view {
	local($no,$sub,$res,$key,$no2,$nam,$eml,$com,$dat,$ho,$pw,$url,%resCountPerPoster,$cut_nam,$is_branching_contents,
		$log_user_id,$log_cookie_a,$log_history_id,$log_useragent,$log_is_private_browsing_mode,$log_first_access_datetime);
	local($job) = @_;

	# アラームを定義
	local($alarm) = int ($m_max * 0.9);

	# スマイルアイコン定義
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
	}

	# 汚染チェック
	$in{'no'} =~ s/\D//g;

	# スレッドログ一括読み込み
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

	# スレッド情報読み込み
	($no,$sub,$res,$key) = @{$log[0]};
	$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
	my $thread_title = $sub; # 本来のスレッドタイトルを記憶
	my $thread_no = $no; # 内部用にスレッド番号を別に記憶
	judge_branch_contents($sub); # 表示内容分岐機能 スレッドタイトル判定

	# カテゴリ名を除いたスレッドタイトルを取得
	my $category_removed_thread_title = $enc_cp932->decode($thread_title);
	foreach my $conv_set_str (@category_convert) {
		my $decoded_conv_set_str = $enc_cp932->decode($conv_set_str);
		my ($keyword) = split(/:/, $decoded_conv_set_str, 2);
		if ($keyword eq '') {
			next;
		}
		local $1; # マッチ変数のスコープを限定
		my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
		if ($category_removed_thread_title =~ /$capture_regex/) {
			# スレッド名をカテゴリ名を除いたもので置き換え
			$category_removed_thread_title = $1;
			last;
		}
	}
	if (Encode::is_utf8($category_removed_thread_title)) {
		$category_removed_thread_title = $enc_cp932->encode($category_removed_thread_title);
	}

    # スレッド閲覧制限機能
    {
		# 日付による除外の判定のため
		# CookieA発行日時 数値表現を作成 (現在のCookieA発行形式に限る)
		my $cookie_a_issue_datetime_num;
		if ($is_cookie_a_issued && $cookie_a =~ /^(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[0-1]))_.._((?:[01]\d|2[0-3])[0-5]\d)$/) {
			$cookie_a_issue_datetime_num = int("$1$2");
		}

		# 日付による除外の判定のため
		# CookieAの文字数を予め取得
		my $cookie_a_length;
		if ($is_cookie_a_issued) {
			$cookie_a_length = length($cookie_a);
		}

        # 判定実施
        my $is_thread_browsing_restrict_user = 0;
        my $disable_setting_flg_char = $enc_cp932->decode('▼');
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

            # 設定無効判定
            if ($setting_set_array[0] eq $disable_setting_flg_char) {
                next;
            }

            # CookieAの有無判定
            if ($setting_set_array[4] eq '1' && $is_cookie_a_issued) {
                # 1がセットされている場合は、CookieA未発行ユーザーのみが判定対象のため、
                # CookieAが存在するユーザーは対象外
                next;
            }

            # ホストとUserAgent・CookieA or 登録ID or 書込IDについて
            # 「-」のみの場合に「」(空)に置き換える
            foreach my $i (2, 3, 6) {
                if ($setting_set_array[$i] eq '-') {
                    $setting_set_array[$i] = '';
                }
            }

            # スレッド名か、
            # ホストとUserAgent・CookieA or 登録ID or 書込IDの両方が空値の場合はスキップ
            if ($setting_set_array[1] eq ''
                || ($setting_set_array[2] eq '' && $setting_set_array[3] eq '')) {
                next;
            }

            # スレッド名判定
            if (!defined($mu->universal_match([$utf8_flagged_category_removed_thread_title], [$setting_set_array[1]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # 一致しないときは次のループへ
                next;
            }

            # ホストとUserAgentの組み合わせ判定
            if ($setting_set_array[2] ne '') {
                my ($host_useragent_match_array) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[2], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array)) {
                    $is_thread_browsing_restrict_user = 1;
                }
            }

            # CookieA or 登録ID or 書込ID判定
            if (!$is_thread_browsing_restrict_user && $setting_set_array[3] ne '') {
                my ($cookiea_userid_historyid_match_array) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $cuser_id, $chistory_id, $setting_set_array[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array)) {
                    $is_thread_browsing_restrict_user = 1;
                }
            }

			# 日付による除外判定
			if ($is_thread_browsing_restrict_user && $is_cookie_a_issued && $setting_set_array[5] ne '') {
				# 設定値の日時比較数値表現配列を作成
				my @reference_datetime_num_array = map {
					$_ =~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/ ? int("$1$2$3$4$5") : ();
				} split(/,/, $setting_set_array[5]);

				# CookieAの文字数で処理を分岐
				if ($cookie_a_length == 14) {
					foreach my $reference_datetime_num (@reference_datetime_num_array) {
						# CookieA発行日時が設定値日時未満である場合は除外対象
						if ($cookie_a_issue_datetime_num < $reference_datetime_num) {
							$is_thread_browsing_restrict_user = undef;
							last;
						}
					}
				} elsif ($cookie_a_length == 12 && scalar(@reference_datetime_num_array) > 0) {
					# CookieAの値が12桁の場合はすべて除外対象
					$is_thread_browsing_restrict_user = undef;
				}
			}

			# CookieA or 登録ID or 書込IDの除外判定
			if ($is_thread_browsing_restrict_user && $setting_set_array[6] ne '') {
				my ($cookiea_userid_historyid_match_array) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $cuser_id, $chistory_id, $setting_set_array[6], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
				if (defined($cookiea_userid_historyid_match_array)) {
					$is_thread_browsing_restrict_user = undef;
				}
			}

			# 判定ループ継続判定
			if ($is_thread_browsing_restrict_user) {
				last;
			}
        }
        # スレッド閲覧制限対象ユーザーの場合はリダイレクト
        if ($is_thread_browsing_restrict_user) {
            print "Location: $thread_browsing_restrict_redirect_url\n\n";
            exit(0);
        }
    }

	# 初回書き込みまでの時間制限機能 判定
	$first_cookie->judge_and_update_cookie(FirstCookie::RESPONSE, $category_removed_thread_title);

	# ユーザ強調表示機能・UserAgentの強調表示機能 ログファイル読み込み
	my %highlight_userinfo_colorindex_hash = {
		'cookie_a'   => {},
		'history_id' => {},
		'host'       => {},
		'user_id'    => {}
	};
	my @highlight_ua_setting_hashref_array;
	if (-s $highlight_userinfo_log_path >= 3) { # 3バイト未満はパースの必要なし
		# ログファイルオープン・読み込み
		open(my $json_log_fh, '<', $highlight_userinfo_log_path) || error("Open Error: $highlight_userinfo_log_path");
		flock($json_log_fh, 1) || error("Lock Error: $highlight_userinfo_log_path");
		seek($json_log_fh, 0, 0);
		local $/;
		my $json_log_contents = <$json_log_fh>;
		close($json_log_fh);

		# JSONパース
		# パースに失敗した (内容に異常がある)場合、内容がなかったものとして取り扱う
		my @load_hightlight_array;
		eval {
			my $json_serializer = JSON::XS->new();
			my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
			if (ref($json_parsed_ref) eq 'ARRAY') {
				@load_hightlight_array = @{$json_parsed_ref};
			}
		};

		foreach my $highlight_hashref (@load_hightlight_array) {
			# 値がハッシュリファレンスではない場合はスキップ
			if (ref($highlight_hashref) ne 'HASH') {
				next;
			}

			# 異常設定値はスキップ
			if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
				|| !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1 || $highlight_hashref->{color} > scalar(@highlight_userinfo_color_name_code)) {
				next;
			}

			# 強調表示タイプを取得
			# (セットされていない場合、ユーザ強調表示とみなす)
			my $type = exists($highlight_hashref->{type}) ? $highlight_hashref->{type} : 1;

			# 強調表示タイプ別に処理
			if ($type == 1) {
				## ユーザ強調表示 ##
				# 設定時間を経過した設定はスキップ
				if (($highlight_hashref->{time} + $highlight_userinfo_hold_hour * 3600) <= $time) {
					next;
				}

				# 項目別にColorインデックスをセット
				foreach my $item_name ('cookie_a', 'history_id', 'host', 'user_id') {
					if (exists($highlight_hashref->{$item_name}) && $highlight_hashref->{$item_name} ne '') {
						$highlight_userinfo_colorindex_hash{$item_name}->{$highlight_hashref->{$item_name}} = int($highlight_hashref->{color}) - 1;
					}
				}
			} elsif ($type == 2) {
				## UserAgentの強調表示 ##
				# Colorインデックス・ホスト・UserAgent・時間による設定有効フラグのハッシュリファレンスとし、配列に追加
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

	# 過去ログ
	if ($job eq "past") {
		$bbsback = "mode=past";
		$guid = "<a href=\"$readcgi?mode=past\">過去ログ</a> &gt; スレッド";

	# 現行ログ
	} else {
		$bbsback = "";
		$guid = "スレッド";
	}

	# 親レス読み込み
	($no2, undef, $nam, $eml, $com, $dat, $ho, $pw, $url, $mvw, $myid, $tim, $upl{1}, $upl{2}, $upl{3}, $idcrypt, $log_user_id, undef,
		$log_cookie_a, $log_history_id, $log_useragent, $log_is_private_browsing_mode, $log_first_access_datetime,
		$upl{4}, $upl{5}, $upl{6}) = @{$log[1]};

	# スレッドタイトルによる書き込み制限機能のスレッド作成者の除外機能
	# >>1の ホスト, URL欄, 登録ID, CookieA, 書込ID を取得
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

	# ID毎投稿数カウント機能 親レス投稿者IDをカウント
	$resCountPerPoster{$idcrypt} = [$no2];

	# NGネーム適用レス名前欄カット表示機能
	($nam, $cut_nam) = &cut_name($nam);

	$com = &auto_link($com, $no);

	# 表示内容分岐機能 親レス判定
	judge_branch_contents($log[1]);

	# タイトルにスレ番号をつける
	if ($showthreadno) {
		$sub="[$in{'no'}] ".$sub;
	}

	# アイコン定義
	if ($job ne "past" && $key eq '0') { $icon = 'fold3.gif'; }
	elsif ($job ne "past" && $key eq '4') { $icon = 'fold3.gif'; }
	elsif ($job ne "past" && $key eq '3') { $icon = 'faq.gif'; }
	elsif ($job ne "past" && $key eq '2') { $icon = 'look.gif'; }
	elsif ($job ne "past" && $res >= $alarm) { $icon = 'fold5.gif'; }
	elsif (time < $tim + $hot) { $icon = 'fold1.gif'; }
	else { $icon = 'fold1.gif'; }

	# ヘッダ
	if ($job eq "past") {
		&header($sub);
	} else {
		&header($sub, "js");
		if ($key eq '0') {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">　　　　　<img src=\"$imgurl/alarm.gif\"> ";
			print "このスレは<b>ロック</b>されています。";
			print "記事の閲覧のみとなります。</td></tr></table>\n";

		} elsif ($key == 2) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">　　　　　<img src=\"$imgurl/alarm.gif\"> ";
			print "このスレは<b>管理人からのメッセージ</b>です。";
			print "</td></tr></table>\n";

		} elsif ($key == 3) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">　　　　　<img src=\"$imgurl/alarm.gif\"> ";
			print "このスレは<b>総合</b>です。";
			print "</td></tr></table>\n";

		} elsif ($key eq '4') {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">　　　　　<img src=\"$imgurl/alarm.gif\"> ";
#			print "このスレは<b>管理人によりロック</b>されています。";
			print "<b>ロック</b>されています。";
			print "</td></tr></table>\n";

		} elsif ($m_max <= $res) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\">　　　　　<img src=\"$imgurl/alarm.gif\"> ";
			print "返信記事数が<b>$res</b>件あります。";
			print "これ以上の書き込みはできません。";
			print "</td></tr></table>\n";
			$key = 0; # 以降を閲覧専用モードとして処理。

		} elsif ($alarm <= $res) {
			print "<table><tr><td width=\"5%\"></td>";
			print "<td width=\"100%\"><img src=\"$imgurl/alarm.gif\"> ";
			print "返信記事数が<b>$res</b>件あります。";
			print "<b>$m_max</b>件を超えると書き込みができなくなります。";
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
    element.focus(); // カーソルを合わせる
}
</script>
<div id="wrapper-main">
<div id="wrapper-main-in">
<div class="crumbs">
<a href="$home">home</a> &gt; <a href="$bbscgi?">$bbsname</a>
</div>


EOM

	# レス読み込み範囲決定
	if ($key == 2) {
		# 管理人メッセージの時はレスを全て表示する
		$l = "$no2-";
	}
	my $all_flg = ($l eq "$no2-"); # レス全表示指定の時はフラグを立てる
	my ($res_range_from, $res_range_to) = split(/-/, $l); # -で分割してレス範囲を決定
	if ($l !~ /\-/) {
		# 範囲指定に'-'がない場合は1つのレスを表示
		$res_range_to = $res_range_from;
	}
	if (!$res_range_from || $res_range_from < $no2) {
		# レス範囲の始めの指定がない場合や、$no2(最初のレスNo)未満のレスNoが指定された時は、
		# 最初のレスをレス範囲始めとする
		$res_range_from = $no2;

		# レス全表示フラグ再チェック
		$all_flg ||= ($l =~ /^\d+-$/);
	}
	if (!$res_range_to || $res_range_to > $res) {
		# レス範囲の終わりの指定がない場合や、最大レスNoより大きい値が指定された時は
		# 最大レスNoをレス範囲終わりとする
		$res_range_to = $res;
	}
	if ($res_range_from > $res_range_to) {
		# $l1(レス範囲始め)が、$l2(レス範囲終わり)よりも小さい場合
		# それぞれ入れ替えて正しい範囲になるよう修正
		($res_range_to, $res_range_from) = ($res_range_from, $res_range_to);
	}

	# レス読み込み範囲内のレスログ配列となるようフィルタリング
	@log = grep { (${$_}[0] >= $res_range_from && ${$_}[0] <= $res_range_to) || ${$_}[0] == $no2; } @log[1..$#log];

	# ページ数計算
	my $page_cnt = int((scalar(@log) - 1) / $t_max);
	my $remainder_res_cnt = (scalar(@log) - 1) % $t_max;
	if (scalar(@log) == 1 || $remainder_res_cnt > 0) {
		# 1レス目のみの表示、もしくは、$t_maxで割り切れないレス数があるときは、
		# ページ数を1増やす
		$page_cnt++;
	}

	# ページ番号決定
	$p = int($p) || 1;
	if ($p <= 0) {
		$p = 1;
	} elsif ($p > $page_cnt) {
		$p = $page_cnt;
	}

	# 全レス表示ではなく、かつ、子レスログが2つ以上ある時は、
	# レス表示範囲のログ配列となるよう、配列をソートしてフィルタリングする
	if (!$all_flg && (scalar(@log) - 1) > 1) {
		# $t_maxレスごとに表示ブロックとしてそのインデックスで降順ソートし(ただし$remainder_res_cnt以下のレスインデックスは除く)、
		# また、表示ブロック内のレスはレスインデックスごとに昇順ソートとする、ログ配列ソート用インデックス配列を作成
		my @sort_indexes =	sort {
			$b > $remainder_res_cnt <=> $a > $remainder_res_cnt
				|| ($b > $remainder_res_cnt && $a > $remainder_res_cnt ? (int(($b - $remainder_res_cnt - 1) / $t_max)) <=> (int(($a - $remainder_res_cnt - 1) / $t_max)) : 0)
				|| $a <=> $b
		} reverse(1..$#log);

		# ソート用インデックス配列を
		# ページ番号に従い、レス表示範囲部分のみの要素となるようフィルタリング
		my $from_index = ($p - 1) * $t_max; # レス表示範囲始め インデックス
		my $to_index = $p * $t_max - 1; # レス表示範囲終わり インデックス
		if ($to_index > $#sort_indexes) {
			# 最大インデックスを超えた$to_indexになってしまうことを防ぐため、いずれか小さい方を採用する
			$to_index = $#sort_indexes;
		}
		@sort_indexes = @sort_indexes[$from_index..$to_index];

		# ログ配列をソート・フィルタリング用インデックス配列でソート
		# (ただし先頭は1レスとするため、常に0が入る)
		@log = @log[0, @sort_indexes];
	}

	# 子レス表示範囲で予め処理を行う必要がある機能のループ処理
	foreach my $res_log_array_ref (@log[1..$#log]) {
		# ID毎投稿数カウント機能 表示範囲内 子レスの同一IDによる投稿をカウント
		my ($res_no, $id) = @{$res_log_array_ref}[0, 15];
		if (exists($resCountPerPoster{$id})) {
			push(@{$resCountPerPoster{$id}}, $res_no);
		} else {
			$resCountPerPoster{$id} = [$res_no];
		}

		# 表示内容分岐機能 子レス判定
		judge_branch_contents($res_log_array_ref);
	}

	# ページ繰越ボタン
	if ($key != 2) {
		print pagelink($thread_no, $page_cnt, $all_flg);
	}

	# スレッド保存フォルダ番号取得
	my $thread_savefolder_number = get_logfolder_number($in{'no'});
	my $thread_savefolder_html = defined($thread_savefolder_number) ? $thread_savefolder_number : '分割無効';

	print <<"EOM";
<!-- google_ad_section_start -->
<h1 class="thread">$sub &nbsp;&nbsp; フォルダ : $thread_savefolder_html</h1>
EOM
	# 表示内容分岐機能 スレッドタイトル表示部分
	if ($is_branching_contents) {
		# 表示範囲のレスに設定した文字列が含まれているか、
		# 画像チェック有効時は、画像がアップされている場合
		print "<h2>表\示1_YES</h2>\n";
	} else {
		# それ以外の場合
		print "<h2>表\示1_NO</h2>\n";
	}

	print <<"EOM";
<div class="main">
<div id="d1">
<dl class=\"hoge\"><dt>
EOM



	# メンテボタン
#	if ($job ne "past") {
#		print "<span class=\"mente\"></span> 1 名前：\n";
#	}
		print "<span class=\"num\"><a onclick=\"dofocus()\" href=\"javascript:MyFace('>>$no2\\n')\" title=\">>$no2\">$no2&nbsp;：</a></span>\n";


	print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam$cut_nam</span> <span class=\"ng_hide\">投稿日：$dat";

# IDを表示
	if($idkey && $idcrypt) {
		print " <span class=\"res_poster_id\">ID: $idcrypt";
		# ID毎投稿数カウント機能 投稿数を出力
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

	# 登録IDを出力
	if ($webprotect_auth_new && $log_user_id ne '') {
		# ユーザ強調表示機能
		if (exists($highlight_userinfo_colorindex_hash{user_id}->{$log_user_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{user_id}->{$log_user_id}]}[1];
			print " 登録ID:<span class=\"user_id\"><span style=\"background-color:$color_code\">$log_user_id</span></span>";
		} else {
			print " 登録ID:<span class=\"user_id\">$log_user_id</span>";
		}
	}

	# 書込IDを出力
	if ($log_history_id ne '') {
		# ユーザ強調表示機能
		# (書込IDに末尾の@が含まれている場合は除いてから検索する)
		(my $find_history_id = $log_history_id) =~ s/\@$//;
		if (exists($highlight_userinfo_colorindex_hash{history_id}->{$find_history_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{history_id}->{$find_history_id}]}[1];
			print " 書込ID:<span style=\"background-color:$color_code\">$log_history_id</span>";
		} else {
			print " 書込ID:$log_history_id";
		}
	}

	# ユニークCookieAを出力
	if ($log_cookie_a ne '') {
		# ユーザ強調表示機能
		if (exists($highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a}]}[1];
			print " CookieA:<span style=\"background-color:$color_code\">$log_cookie_a</span>";
		} else {
			print " CookieA:$log_cookie_a";
		}
	}

    # ホストを出力
	## ユーザ強調表示機能
	if (exists($highlight_userinfo_colorindex_hash{host}->{$ho})) {
		my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{host}->{$ho}]}[1];
		print " ホスト:<span style=\"background-color:$color_code\">$ho</span>";
	} else {
		print " ホスト:$ho";
	}

	# UserAgentを出力
	if ($log_useragent ne '') {
		# UserAgentの強調表示機能
		my $color_code;
		foreach my $setting_hashref (@highlight_ua_setting_hashref_array) {
			if (!$setting_hashref->{valid_flag}) {
				# 時間を経過して無効の設定をスキップ
				next;
			}
			my $target_host = $setting_hashref->{host};
			my $target_useragent = $setting_hashref->{useragent};
			my $color_index = $setting_hashref->{color};

			# 一致判定
			if (defined(${$mu->get_matched_host_useragent_and_whether_its_not_match($ho, $log_useragent, "$target_host<>$target_useragent", undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)}[0])) {
				$color_code = ${$highlight_userinfo_color_name_code[$color_index]}[1];
				last; # 配列の先頭から検索し、最初に一致した設定の色を使用する
			}
		}

		if (defined($color_code)) {
			print " UA:<span style=\"background-color:$color_code\">$log_useragent</span>";
		} else {
			print " UA:$log_useragent";
		}
	}

	# プライベートモードが有効であれば出力
	if ($log_is_private_browsing_mode) {
		print ' プライベートモード:有効';
	}

	# 初回アクセス時間が記録されている場合は出力
	if ($log_first_access_datetime ne '') {
		print " 初回アクセス時間:$log_first_access_datetime";
	}

	# 画像のMD5を出力
	foreach my $i (1 .. 6) {
		my ($image_orig_md5, $image_conv_md5) = (split(/,/, $upl{$i}))[6, 7];
		next if ($image_orig_md5 eq '');

		# 変換前MD5を出力
		print " 画像$i:$image_orig_md5";

		# 変換後MD5が記録されている場合は続けて出力
		if ($image_conv_md5 ne '') {
			print ",$image_conv_md5";
		}
	}

	# 「NGネーム登録」を表示(「NGネーム解除」表示はJavascriptによってページロード後に動的に行われる)
	if($ngname) {
		print " <a href=\"#\" class=\"ngname_toggle ng_toggle\">NGネーム登録</a>";
	}

	# 「NGID登録」を表示(「NGID解除」表示はJavascriptによってページロード後に動的に行われる)
	if($idkey && $idcrypt && $ngid) {
		print " <a href=\"#\" class=\"ngid_toggle ng_toggle\">NGID登録</a>";
	}

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}




print <<"EOM";

EOM

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}

# IDを表示
	if($idkey && $idcrypt) { print ""; }

			print "</dt></dl>\n";


# メール送信フォームへのリンク
	print <<"EOM";
EOM


#名前を変換
#	マッチした文字列の前後を取得($`, $')
#	http://www.perlplus.jp/regular/ref/index2.html

if ($nam =~ /◆.*/){
#  print "<br>前の部分 : $`\n<br>";
#マッチした文字列を代入
  $nam = $`;
#  print "マッチした文字列 : $&\n<br>";
#  print "後の部分 : $'\n<br>";
}
# メール送信フォームへのリンク End


		if ($url) {
			print "<dt>参照： <a href=\"$url\" target=\"_blank\" rel=\"nofollow\">$url</a></dt>\n";
		}

		# コメント出力
		print "\n<div class=\"comment\">$com</div>\n";

		# 画像出力
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
					# サムネイル画像機能が有効かつサムネイル画像ファイルが存在する時
					($width, $height) = &resize($thumb_w, $thumb_h);
					$thumb_path = "$thumburl/$img_folder_number/$tim-${i}_s.jpg";
				} else {
					# オリジナル画像を縮小してサムネイル画像表示する場合
					($width, $height) = &resize($w, $h);
					$thumb_path = "$uplurl/$img_folder_number/$tim-$i$ex";
				}
				# サムネイル画像を表示できる時
				if($thumb_path && $width > 0 && $height > 0) {
					# サムネイル画像およびオリジナル画像へのリンク HTML出力
					print "<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\"><img src=\"$thumb_path\" align=\"top\" border=\"0\" width=\"$width\" height=\"$height\" hspace=\"3\" vspace=\"5\"></a>\n";
					# オリジナル画像ファイル名取得
					push(@img_filename, "■ $img_filename_prefix$img_folder_number/$tim-$i$ex ■");
				}
			} else {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			}
		}

		# 画像ファイル名表示
		if (scalar(@img_filename) > 0) { print "<br><br>\n"; }
		print join("<br>\n", @img_filename) . "\n";
		if ($dd_flg) { print "</div>\n"; }

		# スレッド画面からユーザを制限する機能
		print "<div>\n" . create_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# スレッド画面からユーザを時間制限する機能
		print "<div>\n" . create_restrict_user_by_time_range_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# スレッド画面からユーザを制限する機能 (そのスレのみ)
		print "<div>\n" . create_in_thread_only_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

        # ユーザ強調表示機能
        print "<br><div>\n" . create_highlight_userinfo_form_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "</div><!-- 終了 hoge --></div><!-- 終了 d1 -->\n</div><!-- 終了 main -->\n<!-- 親レス終了 -->\n";

# Google AdSense
	&googleadsense;

	if ($res > 0) {
		print "\n<div class=\"main\">\n";
	}

	# 子レスループ
	foreach (@log[1..$#log]) {
		($no, undef, $nam, $eml, $com, $dat, $ho, $pw, $url, $mvw, $myid, $tim, $upl{1}, $upl{2}, $upl{3}, $idcrypt, $log_user_id, $is_sage,
			$log_cookie_a, $log_history_id, $log_useragent, $log_is_private_browsing_mode, $log_first_access_datetime,
			$upl{4}, $upl{5}, $upl{6}) = @{$_};

		# NGネーム適用レス名前欄カット表示機能
		($nam, $cut_nam) = &cut_name($nam);

		# sage表示
		my $sage;
		if ($is_sage eq '1') {
			$sage = ' [sage] ';
		}

		$com = &auto_link($com, $in{'no'});
#親レス以降
		print "\n\n<!-- レススタート -->\n<div id=\"d$no\"><dl class=\"hoge\"><dt>";


	# メンテボタン
		if ($job ne "past") {
			print "<span class=\"mente\"></span>\n";
		}

		print "<span class=\"num\"><a id=\"$no\"></a><a name=\"$no\"></a><a onclick=\"dofocus()\" href=\"javascript:MyFace('>>$no\\n')\" title=\">>$no\">$no&nbsp;：</a>&nbsp;</span>";
		print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam$cut_nam$sage</span>";
		print " <span class=\"ng_hide\">$dat";

# IDを表示
	if($idkey && $idcrypt) {
		print " <span class=\"res_poster_id\">ID: $idcrypt";
		# ID毎投稿数カウント機能 投稿数を出力
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

	# 登録IDを出力
	if ($webprotect_auth_res && $log_user_id ne '') {
		# ユーザ強調表示機能
		if (exists($highlight_userinfo_colorindex_hash{user_id}->{$log_user_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{user_id}->{$log_user_id}]}[1];
			print " 登録ID:<span class=\"user_id\"><span style=\"background-color:$color_code\">$log_user_id</span></span>";
		} else {
			print " 登録ID:<span class=\"user_id\">$log_user_id</span>";
		}
	}

	# 書込IDを出力
	if ($log_history_id ne '') {
		# ユーザ強調表示機能
		# (書込IDに末尾の@が含まれている場合は除いてから検索する)
		(my $find_history_id = $log_history_id) =~ s/\@$//;
		if (exists($highlight_userinfo_colorindex_hash{history_id}->{$find_history_id})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{history_id}->{$find_history_id}]}[1];
			print " 書込ID:<span style=\"background-color:$color_code\">$log_history_id</span>";
		} else {
			print " 書込ID:$log_history_id";
		}
	}

	# ユニークCookieAを出力
	if ($log_cookie_a ne '') {
		# ユーザ強調表示機能
		if (exists($highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a})) {
			my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{cookie_a}->{$log_cookie_a}]}[1];
			print " CookieA:<span style=\"background-color:$color_code\">$log_cookie_a</span>";
		} else {
			print " CookieA:$log_cookie_a";
		}
	}

	# ホストを出力
	## ユーザ強調表示機能
	if (exists($highlight_userinfo_colorindex_hash{host}->{$ho})) {
		my $color_code = ${$highlight_userinfo_color_name_code[$highlight_userinfo_colorindex_hash{host}->{$ho}]}[1];
		print " ホスト:<span style=\"background-color:$color_code\">$ho</span>";
	} else {
		print " ホスト:$ho";
	}

	# UserAgentを出力
	if ($log_useragent ne '') {
		# UserAgentの強調表示機能
		my $color_code;
		foreach my $setting_hashref (@highlight_ua_setting_hashref_array) {
			if (!$setting_hashref->{valid_flag}) {
				# 時間を経過して無効の設定をスキップ
				next;
			}
			my $target_host = $setting_hashref->{host};
			my $target_useragent = $setting_hashref->{useragent};
			my $color_index = $setting_hashref->{color};

			# 一致判定
			if (defined(${$mu->get_matched_host_useragent_and_whether_its_not_match($ho, $log_useragent, "$target_host<>$target_useragent", undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)}[0])) {
				$color_code = ${$highlight_userinfo_color_name_code[$color_index]}[1];
				last; # 配列の先頭から検索し、最初に一致した設定の色を使用する
			}
		}

		if (defined($color_code)) {
			print " UA:<span style=\"background-color:$color_code\">$log_useragent</span>";
		} else {
			print " UA:$log_useragent";
		}
	}

	# プライベートモードが有効であれば出力
	if ($log_is_private_browsing_mode) {
		print ' プライベートモード:有効';
	}

	# 初回アクセス時間が記録されている場合は出力
	if ($log_first_access_datetime ne '') {
		print " 初回アクセス時間:$log_first_access_datetime";
	}

	# 画像のMD5を出力
	foreach my $i (1 .. 6) {
		my ($image_orig_md5, $image_conv_md5) = (split(/,/, $upl{$i}))[6, 7];
		next if ($image_orig_md5 eq '');

		# 変換前MD5を出力
		print " 画像$i:$image_orig_md5";

		# 変換後MD5が記録されている場合は続けて出力
		if ($image_conv_md5 ne '') {
			print ",$image_conv_md5";
		}
	}

	# 「NGネーム登録」を表示(「NGネーム解除」表示はJavascriptによってページロード後に動的に行われる)
	if($ngname) {
		print " <a href=\"#\" class=\"ngname_toggle ng_toggle\">NGネーム登録</a>";
	}

	# 「NGID登録」を表示(「NGID解除」表示はJavascriptによってページロード後に動的に行われる)
	if($idkey && $idcrypt && $ngid) {
		print " <a href=\"#\" class=\"ngid_toggle ng_toggle\">NGID登録</a>";
	}

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}




		print "";
		if ($eml && $mvw ne '0' && $show_mail==1) {
			print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;";
		}

# IDを表示
	if($idkey && $idcrypt) { print ""; }

			print "</dl></dt>\n";

# メール送信フォームへのリンクStart
	print <<"EOM";
EOM

#名前を変換
#	マッチした文字列の前後を取得($`, $')
#	http://www.perlplus.jp/regular/ref/index2.html

if ($nam =~ /◆.*/){
#  print "<br>前の部分 : $`\n<br>";
#マッチした文字列を代入
  $nam = $`;
#  print "マッチした文字列 : $&\n<br>";
#  print "後の部分 : $'\n<br>";
}

		if ($url) {
			print "<dt>参照： <a href=\"$url\" target=\"_blank\" rel=\"nofollow\">$url</a>\n";
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
					# サムネイル画像機能が有効かつサムネイル画像ファイルが存在する時
					($width, $height) = &resize($thumb_w, $thumb_h);
					$thumb_path = "$thumburl/$img_folder_number/$tim-${i}_s.jpg";
				} else {
					# オリジナル画像を縮小してサムネイル画像表示する場合
					($width, $height) = &resize($w, $h);
					$thumb_path = "$uplurl/$img_folder_number/$tim-$i$ex";
				}
				# サムネイル画像を表示できる時
				if($thumb_path && $width > 0 && $height > 0) {
					# サムネイル画像およびオリジナル画像へのリンク HTML出力
					print "<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\"><img src=\"$thumb_path\" align=\"top\" border=\"0\" width=\"$width\" height=\"$height\" hspace=\"3\" vspace=\"5\"></a>\n";
					# オリジナル画像ファイル名取得
					push(@img_filename, "■ $img_filename_prefix$img_folder_number/$tim-$i$ex ■");
				}
			} else {
				print "[<a href=\"$uplurl/$img_folder_number/$tim-$i$ex\" target=\"_blank\">$tim-$i$ex</a>]\n";
			}
		}
		# 画像ファイル名表示
		if (scalar(@img_filename) > 0) { print "<br><br>\n"; }
		print join("<br>\n", @img_filename) . "\n";
		if ($dd_flg) { print "</div>\n"; }

		# スレッド画面からユーザを制限する機能
		print "<div>\n" . create_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# スレッド画面からユーザを時間制限する機能
		print "<div>\n" . create_restrict_user_by_time_range_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "<br>\n";

		# スレッド画面からユーザを制限する機能 (そのスレのみ)
		print "<div>\n" . create_in_thread_only_restrict_user_link_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

        # ユーザ強調表示機能
        print "<br><div>\n" . create_highlight_userinfo_form_html($log_cookie_a, $log_history_id, $ho, $log_user_id) . "</div>\n";

		print "</div>\n<!-- レス終了-->\n";


	}

	print "<tr><td><br></td></tr>" if (!$i);
# メール送信フォームへのリンクEnd



	print <<"EOM";
<!-- google_ad_section_end -->
<!-- 終了 main -->
EOM
	# ページ繰越ボタン
	if ($key != 2 && scalar(@log) > 1) {
		print pagelink($thread_no, $page_cnt, $all_flg);
	}

	# 現行ログ/過去ログ ページ下部 共通表示項目定義
	my $common_display_contents_at_bottom_of_page = '';
	{
		# スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能 リンク表示部
		$common_display_contents_at_bottom_of_page .= "<br><br>\n";
		for (my $i = 1; $i <= 6; $i++) {
			$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC
		}
		$common_display_contents_at_bottom_of_page .= <<"EOC";
EOC


		## スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能 リンク表示部
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


		## ユーザ制限機能 (CookieAなどをフォームから登録) フォーム表示部
		$common_display_contents_at_bottom_of_page .= "<br><br>\n";
		# CSV一括入力フォーム
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
<br>
EOC
		# 項目別入力フォーム
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC


		## ユーザ強調表示機能 (CookieAなどをフォームから登録) フォーム表示部
		$common_display_contents_at_bottom_of_page .= "<br><br><br>\n";
		# CSV一括入力フォーム
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</select>
</div>
<br>
EOC
		# 項目別入力フォーム
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC


		## UserAgentの強調表示機能 (ホストとUserAgentをフォームから登録) フォーム表示部
		# 登録フォーム
		$common_display_contents_at_bottom_of_page .= <<"EOC";
<div>
EOC
		$common_display_contents_at_bottom_of_page .= <<"EOC";
</div>
EOC
		# 現在設定プルダウンリスト 更新/削除フォーム
		# (設定が1つ以上ある場合のみ表示)
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
<button type="button" id="highlight_ua_form_current_settings_update_timestamp">更新</button>
<span class="highlight_ua_form_current_settings_ajax_messages" id="highlight_ua_form_current_settings_update_timestamp_ajax_message"></span>
&nbsp;
<button type="button" id="highlight_ua_form_current_settings_remove">削除</button>
<span class="highlight_ua_form_current_settings_ajax_messages" id="highlight_ua_form_current_settings_remove_ajax_message"></span>
</div>
EOC
		}


		## 表示内容分岐機能 ページ下部表示部分
		if ($is_branching_contents) {
			# 表示範囲のレスに設定した文字列が含まれているか、
			# 画像チェック有効時は、画像がアップされている場合
			$common_display_contents_at_bottom_of_page .= "<h2>表\示2_YES</h2>\n";
		} else {
			# それ以外の場合
			$common_display_contents_at_bottom_of_page .= "<h2>表\示2_NO</h2>\n";
		}
	}

	if ($job ne "past" && ($key == 1 || $key == 3) && $ReadOnly == 0) {
		# 現行ログでスレッドロックされていない時、レスフォーム表示
		&form2('', $thread_title, \%first_res, $common_display_contents_at_bottom_of_page);
	} else {
		# 過去ログかスレッドロックされているなど、レス書き込みできない時

		# ページ下部 共通表示項目を出力
		print $common_display_contents_at_bottom_of_page;
	}
	print <<"EOM";

</div><!--終了 wrapper-main-in-->
</div><!--終了 wrapper-main-->


</div><!-- 終了 container -->




EOM



	print <<"EOM";



</ul>
</div><!-- 終了 header_s -->





</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  個別記事閲覧
#-------------------------------------------------
sub view2 {
	# スマイルアイコン定義
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
	}

	# 汚染チェック
	$in{'f'}  =~ s/\D//g;

	# 記事No認識
	if ($in{'no'} =~ /^\d+$/) { $ptn = 1; $start = $in{'no'}; }
	elsif ($in{'no'} =~ /^(\d+)\-$/) { $ptn = 2; $start = $1; }
	elsif ($in{'no'} =~ /^(\d+)\-(\d+)$/) { $ptn = 3; $start = $1; $end = $2; }
	else { &error("記事Noが不正です"); }

	# スレッドログファイルパス取得
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";

	unless (-e $logfile_path) {
		 &error("スレが見当たりません");
	}

	# 自分の投稿を目立たせる機能 有効状態取得
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
    element.focus(); // カーソルを合わせる
}
</script>


<div id="container">


<div id="wrapper-main">
<div id="wrapper-main-in">



EOM


#スレ名を取得
#	local($flag, $top);
	local $top;
	open(IN, $logfile_path);
	$top = <IN>;
	local($no3,$sub,$res,$key) = split(/<>/, $top);
	$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

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

		# 記事表示

		if ($eml && $mvw ne '0' && $show_mail==1) {
			print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
		}


print "\n\n<!-- レススタート -->\n<dl class=\"hoge\"><dt>";




	# メンテボタン
	if ($job ne "past") {
		print "<span class=\"mente\"></span><span class=\"num\">$no </span> \n";
	}

	print "<span class=\"link_name" . ($highlight_name_in_own_post && $log_history_id ne '' && $log_history_id eq $chistory_id ? '2' : '1') . "\">$nam</span>  $dat";

	if ($eml && $mvw ne '0' && $show_mail==1) {
		print "&nbsp; &lt;<a href=\"mailto:$eml\" class=\"num\">$eml</a>&gt;\n";
	}



# IDを表示
	if($idkey && $idcrypt) { print ""; }
			print "</dt></dl>\n";

#親レスの名前欄




		$com = &auto_link($com, $in{'f'});

		print "<div class=\"comment\">$com</div>\n";

		if (($ptn == 3 && $end == $no) || ($flag && $ptn == 1)) { last; }
	}
	close(IN);

	if (!$flag) {
		print "<h3>記事が見当たりません</h3>\n";
	}

	print <<"EOM";


</div><!--終了 wrapper-main-in-->
</div><!--終了 wrapper-main-->



</div><!-- 終了 container -->


</body>
</html>
EOM
	exit;
}


#-------------------------------------------------
#  新規フォーム
#-------------------------------------------------
sub form {

	if ($ReadOnly) {
		&error("$Oshirase");
	}

	# 権限チェック
	if ($authkey && $my_rank < 2) {
		&error("投稿の権限がありません");
	}

	# ヘッダ
	if ($smile) { &header("", "js"); }
	else { &header(); }

	print <<"EOM";
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<div align="center">
<table width="95%">
<tr>
  <td align="right" nowrapper-main>
	<a href="$bbscgi?">トップページ</a> &gt; 新規スレッド作成
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>新規スレッド作成フォーム</b></td>
</tr></table></Td></Tr></Table>
EOM

	&form2("new");

	print "</div></body></html>\n";
	exit;
}

#-------------------------------------------------
#  フォーム内容
#-------------------------------------------------

#-------------------------------------------------
sub form2 {
	# 返信投稿時(プレビュー含む)は、$thread_title、%first_resのハッシュリファレンス、ページ下部表示HTML(スレッド表示時のみ)を引数に渡す
	my ($job, $thread_title, $first_res_hash_ref, $common_display_contents_at_bottom_of_page) = @_;

	# フォーム表示を行うかどうかのフラグ初期化(デフォルトでは表示)
    my $display_form = 1;

	# スレッドタイトルによる書き込み制限機能で使用する1レス情報ハッシュ(返信投稿・プレビュー時のみ使用)
	# ハッシュリファレンスをデリファレンス
	my %first_res;
	if (defined($first_res_hash_ref)) {
		%first_res = %{$first_res_hash_ref};
	}

	# 権限チェック
	if ($authkey && $my_rank < 2) {
		return;
	}

	# クッキー取得
	local($cnam,$ceml,$cpwd,$curl,$cmvw,undef,$cuser_pwd,$cthread_sort,$cthread_sage,$csave_history,$cincrease_upload_num_checked) = &get_cookie;
	if ($in_url==0 || $in_url==1){
	if ($curl eq "") { $curl = "http://"; }
	}

	# プレビュー用にクッキー情報を上書き
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
	# プレビューじゃないときは編集不可能オプションを無効に
		$editpreview='';
	}
#		$editpreview='';

	# 初回書き込みまでの時間制限機能
	if ((my $left_hours = $first_cookie->get_left_hours_of_restriction()) > 0) {
		$display_form = 0;
		my $restrict_hours = $first_cookie->get_hours_of_restriction();
		if ($job eq 'new' || $job eq 'preview') {
			print <<"EOM";
<h3 style=\"color: #ff0000;\">スレッド作成が可能\になるまであと${left_hours}時間です。●${restrict_hours}</h3>
EOM
		} else {
			print "<h3 style=\"color: #ff0000;\">レスが可能\になるまであと${left_hours}時間です。●${restrict_hours}</h3>\n";
		}
	}

	# 外部ファイルによるスレッド作成制限機能などの統合 インスタンス初期化
	my $thread_create_post_restrict = ThreadCreatePostRestrict->new(
		$mu,
		$thread_create_post_restrict_settings_filepath,
		$host, $useragent, $cookie_a, $cuser_id, $chistory_id, 0,
		$cookie_a_instance
	);

	# スレッド作成制限機能
	if ($job eq 'new' || $job eq 'preview') {
		# 外部ファイルによるスレッド作成制限機能などの統合 スレッド作成制限機能 制限状態取得
		my $thread_create_restrict_status = $thread_create_post_restrict->determine_thread_create_restrict_status();

		my $err_msg_html;
		if ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a, $cuser_id, $chistory_id, $host) # スレッド画面からユーザを制限する機能
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a, $cuser_id, $chistory_id, $host) # スレッド画面からユーザを時間制限する機能
		) {
			$display_form = 0;
			$err_msg_html = "このホストからスレッド作成はできません。";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_2) {
			$display_form = 0;
			$err_msg_html = "このホストからスレッド作成はできません。(リンク先のhogehogeではスレッド作成ができます。)";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_3) {
			$display_form = 0;
			$err_msg_html = "スレッドの作成は出来ません。●●";
		} elsif ($thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_4) {
			$display_form = 0;
			$err_msg_html = "スレッドの作成は出来ません。▲▲";
		} elsif (!$webprotect_auth_new
			&& $thread_create_restrict_status & ThreadCreatePostRestrict::RESULT_THREAD_CREATE_RESTRICT_TYPE_5) {
			# 強制的にWebProtectによる登録ID認証を行わせる
			$webprotect_auth_new = 1;
		}
		# エラーメッセージがある場合は表示する
		if ($err_msg_html) {
			print <<"EOM"
<h3 style=\"color: #ff0000;\">$err_msg_html</h3>
EOM
		}
	}

	# スレッドタイトルによる書き込み制限機能(レスフォーム表示時のみ)
	if ($display_form && ($job eq '' || $job eq 'resview')) {
		# 外部ファイルによるスレッド作成制限機能などの統合 スレッドタイトルによる書き込み制限機能 制限状態取得
		my $post_restrict_status = $thread_create_post_restrict->determine_post_restrict_status_by_thread_title(
			$thread_title, $first_res{'host'}, $first_res{'url'}, $first_res{'user_id'}, $first_res{'cookie_a'}, $first_res{'history_id'}
		);

		my $msg;
		if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1
			|| $mu->is_restricted_user_from_thread_page($cookie_a, $cuser_id, $chistory_id, $host) # スレッド画面からユーザを制限する機能
			|| $mu->is_restricted_user_from_thread_page_by_time_range($cookie_a, $cuser_id, $chistory_id, $host) # スレッド画面からユーザを時間制限する機能
			|| $mu->is_in_thread_only_restricted_user_from_thread_page($in{'no'}, $cookie_a, $cuser_id, $chistory_id, $host) # スレッド画面からユーザを制限する機能 (そのスレのみ)
		) {
			$msg = "<h3 style=\"color: #ff0000;\">このホストから、このスレッドへの書き込みは出来ません。</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2) {
			$msg = "<h3 style=\"color: #ff0000;\">このホストから、このスレッドへの書き込みは出来ません。<br>リンク先のhogehogeでは書き込めます。</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3) {
			$msg = "<h3 style=\"color: #ff0000;\">このスレッドへの書き込みは出来ません。●●</h3>\n";
		} elsif ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4) {
			$msg = "<h3 style=\"color: #ff0000;\">このスレッドへの書き込みは出来ません。▲▲</h3>\n";
		} elsif (!$webprotect_auth_res
			&& $post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5) {
			# 強制的にWebProtectによる登録ID認証を行わせる
			# (書き込みフォーム非表示や警告文表示は行わない)
			$webprotect_auth_res = 1;
			$msg = '';
		}
		if (defined($msg)) {
			if ($post_restrict_status & ThreadCreatePostRestrict::RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION) {
				# スレッド作成者の除外機能
				# スレッド作成者と判定され、>>1のURL欄にjogaiと指定されているとき
				print "<h3 style=\"color: #ff0000;\">スレッド作成者の場合は書き込みが出来ます。</h3>\n";
			} elsif ($msg ne '') {
				# スレッド作成者以外か、>>1のURL欄にjogaiと指定されていない場合は、
				# 書き込みフォーム非表示と警告文表示を行う
				$display_form = 0;
				print $msg;
			}
		}
	}

	# 書き込みできるホストでのみ、フォームを表示
	if ($display_form) {
        # ホストなどによる画像アップロードの無効
        my $show_image_upl_buttons = $image_upl;
		$show_image_upl_buttons &&= !$mu->is_disable_upload_img($thread_title, $host, $useragent, $cookie_a, $cuser_id, $chistory_id, 0, \@disable_img_upload);

        # ホストなどによるageの無効
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
題名
<input type="text" name="sub" size="10" value="" maxlength="10"> <font color="$col4">内容を表\す題名をつけてください</font>
EOM
			$submit = 'スレッドを生成';
		} elsif ($job eq "resview") {
			print <<EOM;
  題名
<input type="text" name="sub" size="10" value="t" maxlength="10"> <font color="$col4">内容を表\す題名をつけてください</font>
EOM
			$submit = '返信する';
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
  題名
<input type=\"input\" name=\"sub\" size=\"10\" value=\"\" maxlength=\"10\">

<br><br>
カテゴリ：<br>
<input type="radio" name="add_sub" value="" checked>デフォルト<br>
<input type="radio" name="add_sub" value="_cate1">カテゴリ1<br>
<input type="radio" name="add_sub" value="_cate2">カテゴリ2
EOM
				$submit = 'スレッドを生成';
			} else {
				print <<EOM;
  題名
タイトルは次の画面で設定してください
EOM
				$submit = 'プレビュー';
			}
		} else {
			# レスの場合の処理
			# 		print <<EOM;
			#   題名
			# <input type="text" name="sub" size="10" value="$resub" maxlength="10">
			# EOM
			print <<EOM;
  題名
EOM
			if ($restitle) {
				print "<input type=\"input\" name=\"sub\" size=\"3\" value=\"t\" maxlength=\"3\">\n";
				$submit = ' 返信する ';
                if ($show_sage_checkbox) {
                    print "<input type=\"checkbox\" name=\"sage\" value=\"1\"";
                    if ($cthread_sage eq '1') { print " checked"; }
                    print ">sage\n";
                } else {
                    print "<input type=\"hidden\" name=\"sage\" value=\"1\">\n";
                }
			} else {
				print "タイトルは次の画面で設定してください\n";
				$submit = ' 返信のプレビュー ';
			}
			print "<input type=\"hidden\" name=\"res\" value=\"$in{'no'}\">\n";
			print "<input type=\"hidden\" name=\"l\" value=\"$in{'l'}\">\n";
		}

		print <<"EOM";
<br>名前
EOM
		# 名前欄非表示機能 (レスフォーム表示時のみ)
		if (($job ne '' && $job ne 'resview') || !$mu->is_hide_name_field_in_form($thread_title, \@hide_form_name_field)) {
			print "    <input type=\"text\" name=\"name\" size=\"10\" value=\"$cnam\" maxlength=\"20\"><br>「名前#任意の文字列」でトリップ生成\n";
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
					@mvw = ('非表示','表示');
					foreach (0,1) {
						if ($cmvw == $_) {
							print "<option value=\"$_\" selected>$mvw[$_]\n";
						} else {
							print "<option value=\"$_\">$mvw[$_]\n";
						}
					}
					print "</select>\n";
				} elsif ($usermail) {
					print "  <input type=\"hidden\" name=\"mvw\" value=\"0\"> 入力すると <img src=\"$imgurl/mail.gif\" alt=\"メールを送信する\" width=\"16\" height=\"13\" border=\"0\"> からメールを受け取れます（アドレス非表\示）\n";
					if ($mailnotify==1 && $job eq "new") {
						print "スレッド作成者にはレスがついた場合、メールでお知らせします\n";
					} elsif ($mailnotify==2) {
						print "また、書き込みをしたスレッドにレスがついた場合、メールでお知らせします\n";
					}
				} else {
				}
				if ($in_mail == 3) {
					print " 迷惑投稿防止のため何か入れると投稿できません\n";

				} elsif ($in_mail == 1) {
					print " （必須）\n";
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
				print " 必ず何か入力しないと投稿できません\n";
			}
			if ($in_url==3){
				print " 迷惑投稿防止のため何か入れると投稿できません\n";
			}

			print <<EOM;
EOM

		}

		# 画像フォーム
		if ($image_upl && ($job eq "preview" || $job eq "resview" || $restitle && ($job eq 'new' || $job eq ""))) {
			print "<b>画像添付</b><br><span style=\"font-size:9px\">";
			print join('/', map { $_ =~ s/^\.//; uc($_); } sort(grep { $imgex{$_}; } keys(%imgex)));
			if ($show_image_upl_buttons) {
				if ($upl_increase_num > 0) {
					print "<input type=\"hidden\" name=\"increase_num\" value=\"0\">\n";
					print '<input type="checkbox" name="increase_num" id="increase_upload_num_checkbox" value="1"';
					if ($cincrease_upload_num_checked) {
						print ' checked';
					}
					print "> 4枚以上<br>\n";
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
			print "<b>画像添付</b><br><span style=\"font-size:9px\">";
			print join('/', map { $_ =~ s/^\.//; uc($_); } sort(grep { $imgex{$_}; } keys(%imgex)));

		}
		# 力技で展開
		#			print "<input type=\"file\" name=\"upfile1\" value=\"$in{'upfile1'}\" size=\"45\"><br>\n";
		#			print "<input type=\"file\" name=\"upfile2\" value=\"$in{'upfile2'}\" size=\"45\"><br>\n";
		#			print "<input type=\"file\" name=\"upfile3\" value=\"$in{'upfile3'}\" size=\"45\"><br>\n";


		print <<EOM;
パスワード
  <input type="password" name="pwd" size="8" value="$cpwd" maxlength="8">
   （記事メンテ時に使用）
EOM
		if(($webprotect_auth_new && ($job eq "new" || $job eq "preview")) || $webprotect_auth_res && ($job eq "" || $job eq "resview")) {
			print <<EOM;
登録ID
  <input type="text" name="user_id" size="30" value="$cuser_id">
登録パスワード
  <input type="password" name="user_pwd" size="30" value="$cuser_pwd">
EOM
        }

		# reCAPTCHA認証表示判定
		my $is_recaptcha_enabled = 0;
		if ($recaptcha_thread && (($restitle && $job eq "new") || (!$restitle && $job eq "preview"))) {
			# スレッド作成時
			# 消去ログオープン
			my $create_log_fh;
			if (open($create_log_fh, '<', $recaptcha_thread_create_log) && flock($create_log_fh, 1)) {
				# 削除ログ行数カウント
				my $create_count = 0;
				while (sysread $create_log_fh, my $buffer, 4096) {
					$create_count += ($buffer =~ tr/\n//);
				}
				$create_count--; # 先頭行分を差し引き
				if ($create_count + 1 > $recaptcha_thread_permit) {
					# スレッド連続作成許容数を超えて書き込みしようとしているため、reCAPTCHA認証を有効
					$is_recaptcha_enabled = 1;
				}
				close($create_log_fh);
			}

			# reCAPTCHA認証対象ホストログオープン
			# ホストが一致する場合は更新、それ以外でも認証対象の場合は追記する
			my $auth_host_log_fh;
			if (open($auth_host_log_fh, '+>>', $recaptcha_thread_auth_host_log) && flock($auth_host_log_fh, 2) && seek($auth_host_log_fh, 0, 0)) {
				my $auth_host_log = "日時,スレッドタイトル,ホスト,タイムスタンプ\n";
				<$auth_host_log_fh>; # 先頭行読み飛ばし
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
			# レス時はログによる表示判定を行わず、設定値のみで切り替える
			$is_recaptcha_enabled = $recaptcha_res && (($restitle && $job eq "") || (!$restitle && $job eq "resview"));
		}

		# 投稿キー
		if ($is_recaptcha_enabled) {
			print <<"EOM"
投稿キー
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

			# キー生成
			require $regkeypl;
			local($str_plain,$str_crypt) = &pcp_makekey;

			# 入力フォーム
			print qq |投稿キー|;
			print qq |<input type="text" name="regikey" size="6" style="ime-mode:inactive">\n|;
			print qq |（投稿時 <img src="$registkeycgi?$str_crypt" align="absmiddle" alt="投稿キー"> を入力してください）\n|;
			print qq |<input type="hidden" name="str_crypt" value="$str_crypt">\n|;
			#	}
			#	if ($regist_key && $job eq "preview") {
		} elsif ($regist_key_new && $job eq "preview" || ($regist_key_res && $job eq "resview")) {

			if ($in{'regikey'} eq "") {
				require $regkeypl;
				local($str_plain,$str_crypt) = &pcp_makekey;
				$in{'str_crypt'}=$str_crypt;
			}

			print qq |投稿キー|;
			print qq |<input type="text" name="regikey" size="6" value="$in{'regikey'}" style="ime-mode:inactive">\n|;
			print qq |（投稿時 <img src="$registkeycgi?$in{'str_crypt'}" align="absmiddle" alt="投稿キー"> を入力してください）\n|;
			print qq |<input type="hidden" name="str_crypt" value="$in{'str_crypt'}">\n|;
		}

		print <<EOM;
コメント
EOM

		# アイコン
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

		# 新規スレはテンプレ展開
		if ($job eq "new") {
			print "$createtemplate\n";
		}
		# プレビュー時
		if ($job eq "preview" || $job eq "resview" ) {
			print "$i_com";
		}

		print <<"EOM";
</textarea>
<br>
    <input type="submit" value="$submit"> &nbsp;&nbsp;
    <input type="checkbox" name="cook" value="on" checked>クッキー保存 &nbsp;&nbsp;
EOM
		#プレビュー機能を無効時（$restitle = 1;）、スレッド作成画面に「確認」のチェックボックスを表示します。
		if($restitle && $in{'mode'} eq 'form') {
			print<<"EOM";
			<input type="checkbox" name="confirm" value="on">確認
EOM
	}
	print<<"EOM";

  </form>
EOM

        # 書き込み履歴に記録チェックボックス(書込ID発行ページヘのリンク)
		if ($job eq "new") {
			print '';
		}
		if (defined($chistory_id)) {
			# チェックボックスにチェックを入れない場合の送信値
			print "<input type=\"hidden\" name=\"save_history\" value=\"0\">\n";
		}
        print "<input type=\"checkbox\" name=\"save_history\" value=\"1\"";
        if (!defined($chistory_id)) {
            print ' disabled';
        } elsif ($csave_history == 1 || $csave_history eq '') {
			print ' checked';
		}
        print '> 記録（';
        if (defined($chistory_id)) {
            print "ID：$chistory_id";
        } else {
            print "<a href=\"$history_webprotect_issue_url\">【書込ID発行】</a>";
            print "<div style=\"text-align: right\"><a href=\"./admin.cgi?action=log&file=$in{'no'}\">ログの閲覧</a></div>";
        }
		if ($job eq "new") {
			print "）\n";
		} else {
			print "）<br>\n";
		}
	}

	if ($job ne "preview" && $job ne "new") {
		# ページ下部 共通表示項目を出力
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
#  過去ログ閲覧
#-------------------------------------------------
sub past {
	# 記事閲覧
	if ($in{'no'}) { &view("past");	}

	&header();
	print <<"EOM";
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%"><tr><td align="right" nowrapper-main>
<a href="$bbscgi?">トップページ</a> &gt; 過去ログ
</td></tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1" class="td0">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/memo1.gif" align="middle">
&nbsp;<b>過去ログ</b></td>
</tr></table></Td></Tr></Table>

<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="16"><br></td>
  <td bgcolor="$col2" width="80%"><b>スレ</b></td>
  <td bgcolor="$col2" nowrapper-main><b>投稿者</b></td>
  <td bgcolor="$col2" nowrapper-main><b>返信数</b></td>
  <td bgcolor="$col2" nowrapper-main><b>最終更新</b></td>
</tr>
EOM

	# スレ展開
	local($i) = 0;
	if ($p eq "") { $p = 0; }
	# カテゴリ表示機能の有効状態によって処理順を変更するため、
	# ログ読み取り時の各処理をサブルーチン化する
	my $countLog = sub {
		# 対象ログとして件数カウントし、表示対象外の場合スキップする
		$i++;
		next if ($i < $p + 1);
		last if ($i > $p + $menu2);
	};
	my $readLog = sub {
		# ログを読み取り、各項目を変数に代入してリストで返す
		chomp($_);
		($no,$sub,$res,$name,$date,$host) = (split(/<>/))[0..4,10];
		$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
	};
	my $judgeCategory = sub {
		next if $sub !~ /$in{'k'}$/; # タイトル末尾にカテゴリ名を含まない場合はスキップする
	};
	open(IN,"$pastfile") || &error("Open Error: $pastfile");
	while (<IN>) {
		local ($no,$sub,$res,$name,$date,$host);

		# ログ読み取り処理実行
		if ($in{'k'} eq '') {
			# カテゴリ表示機能 無効時
			$countLog->();
			$readLog->();
		} else {
			# カテゴリ表示機能 有効時
			$readLog->();
			$judgeCategory->();
			$countLog->();
		}

		# スレッド一覧ログファイルにスレッド作成者ホスト名の記録がない場合
		# スレッドログファイルより読み込み（旧スレッド一覧ログファイルフォーマットとの互換性のための実装)
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
	# 残りの表示範囲外のスレッド件数カウント
	if ($in{'k'} eq '') {
		# カテゴリ表示機能無効時はバッファに一斉に読み込み改行をカウント
		local $/ = undef;
		my $buffer = <IN>;
		$i += ($buffer =~ tr/\n//);
	} else {
		# 有効時は1行ずつタイトル末尾が一致するか確認してカウント
		while(<IN>) {
			chomp($_);
			(my $sub = (split(/<>/))[1]) =~ s/\0*//g;
			$i++ if $sub =~ /$in{'k'}$/;
		}
	}
	close(IN);

	if (!$i) {
		print "<td bgcolor=\"$col2\"></td>";
		print "<td colspan=\"4\" bgcolor=\"$col2\">- 現在過去ログはありません -</td>\n";
	}

	print "</table></Td></Tr></Table>\n";

    # ページ移動ボタン表示
    if ($p - $menu2 >= 0 || $p + $menu2 < $i) {
        print "<br><br><table>\n";

        # 現在表示ページ/全ページ数表示
        my $pages = int(($i - 1) / $menu2) + 1; # 全ページ数取得
        if ($p < 0) {
            # マイナスが指定された時は、1ページ目とする
            $p = 0;
        } elsif ($p + 1 > $i) {
            # 全スレッド件数より大きい値が指定された時は、最終ページ指定とする
            $p = ($pages - 1) * $menu2;
        }
        my $current_page = int($p / $menu2) + 1; # 現在表示ページ取得
        print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

        # 1ページ目・前後ページ・最終ページへのリンク
        my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
        print "<tr><td class=\"num\">";
        if ($current_page <= 1) {
            print "&lt;&lt;　前へ　";
        } else {
            my $prev_page = ($current_page - 2) * $menu2;
            print "<a href=\"$readcgi?mode=past&${k_html}p=0\">&lt;&lt;</a>　<a href=\"$readcgi?mode=past&${k_html}p=$prev_page\">前へ</a>　";
        }
        if ($current_page >= $pages) {
            print "次へ　&gt;&gt;";
        } else {
            my $next_page = $current_page * $menu2;
            my $last_page = ($pages - 1) * $menu2;
            print "<a href=\"$readcgi?mode=past&${k_html}p=$next_page\">次へ</a>　<a href=\"$readcgi?mode=past&${k_html}p=$last_page\">&gt;&gt;</a>";
        }
        print "</td></tr>\n";

        print "</table>\n";
    }

	print <<"EOM";
</div><!--終了 wrapper-main-in-->
</div><!--終了 wrapper-main-->



EOM

	print "</div><!-- 終了 container -->\n</body></html>\n";
	exit;
}


#-------------------------------------------------
#  ページ繰越ボタン
#-------------------------------------------------
sub pagelink {
	my ($thread_no, $page_cnt, $all_flg) = @_;

    # テーブルブロック始め
	my $pglog .= "<table>\n";

    # 全レス表示フラグが立っていない時のみ、ページ移動リンクを表示
    if (!$all_flg) {
        # 現在表示ページ/全ページ数表示
        $pglog .= "<tr><td class=\"num\" align=\"center\">$p/$page_cnt</td></tr>\n";

        # 1ページ目・前後ページ・最終ページへのリンク
        my $l_html = exists($in{l}) ? "&l=$in{l}" : "";
        $pglog .= "<tr><td class=\"num\" align=\"center\">";
        if ($p <= 1 || $all_flg) {
            $pglog .= "&lt;&lt;　前へ　";
        } else {
            my $prev_page = $p - 1;
            $pglog .= "<a href=\"$readcgi?no=$thread_no&p=1$l_html\">&lt;&lt;</a>　<a href=\"$readcgi?no=$thread_no&p=$prev_page$l_html\">前へ</a>　";
        }
        if ($p >= $page_cnt || $all_flg) {
            $pglog .= "次へ　&gt;&gt;";
        } else {
            my $next_page = $p + 1;
            $pglog .= "<a href=\"$readcgi?no=$thread_no&p=$next_page$l_html\">次へ</a>　<a href=\"$readcgi?no=$thread_no&p=$page_cnt$l_html\">&gt;&gt;</a>";
        }
		# 1つ目のtd閉じタグの次の空tdタグは「ここまで読んだ機能」操作結果表示セルの内容変化により
		# ページ移動リンクの表示位置を変化させないための調整用ダミーセルです
        $pglog .= "</td><td></td></tr>\n";
    }

    # 状況表示・その他リンク
    $pglog .= "<tr><td class=\"num\">\n";
    if ($all_flg) {
        # 全レス表示フラグが立っている時
        $pglog .= "（全部表\示中） <a href=\"$readcgi?no=$thread_no\">もどる</a>\n";
    } else {
        $pglog .= "<a href=\"$readcgi?no=$thread_no&l=$no2-\">全部表\示</a>\n";
    }
	$pglog .= "<a href=\"$bbscgi\">スレッド一覧</a>\n";
	if (!$createonlyadmin) {
		$pglog .= "<a href=\"$readcgi?mode=form\">新規スレッド作成</a>\n";
	}

	# ここまで読んだ機能 リンク
	$pglog .= "<a href=\"#\" class=\"readup_here\" data-threadno=\"$thread_no\">お気に入り</a></td>\n";
	$pglog .= "<td class=\"num readup_here_op_result\"></td>\n";

	$pglog .= "</tr>\n";

    # テーブルブロック終わり
    $pglog .= "</table>\n";

	return $pglog;
}

#-------------------------------------------------
#  リンク処理
#-------------------------------------------------
sub auto_link {
	local($msg, $f) = @_;
	local($1, $2, $3, $4, $5); # 呼び出し元からのマッチ変数混入を回避

	$msg =~ s/([^=^\"]|^)(http[s]?\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
#	$msg =~ s/([^=^\"]|^)(https\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\">$2<\/a>/g;
# レスNo指定（表示系未実装））
#	$msg =~ s/&gt;&gt;(\d)([\d\-]*)/<a href=\"$script?mode=view2&f=$f&no=$1$2\" target=\"_blank\">&gt;&gt;$1$2<\/a>/gi;
# 他スレ参照 by あらら
#	$msg =~ s/&gt;&gt;\[(\d+)\](-?)([\d]?)([\d\-]*)([^<&]*)/<a href=\"$script?mode=view&no=$1&l=$3$4\" target=\"_blank\">&gt;&gt;[$1]$2$3$4$5<\/a>/gi;
	if ($showthreadno) {
	$msg =~ s/&gt;&gt;\[(\d+)\](-)([\d]?)([\d\-]*)([^<&]*)/<a href=\"$readcgi?no=$1&l=$3$4\" target=\"$target\">&gt;&gt;[$1]$2$3$4$5<\/a>/gi;
	$msg =~ s/&gt;&gt;\[(\d+)\]([^\-][^<&\-]*)/<a href=\"$readcgi?no=$1\" target=\"$target\">&gt;&gt;[$1]$2<\/a>/gi;
	}
# 他スレ参照（スレを参照するのみの簡易版・表示系が未実装のため）
#	$msg =~ s/&gt;&gt;\[(\d+)\]([^<&]*)/<a href=\"$readcgi?no=$1\" target=\"$target\">&gt;&gt;[$1]$2<\/a>$3/gi;
# bctpリンク （BitComet用）
#	$msg =~ s/([^=^\"]|^)(bctp\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,\|]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
# bcリンク （BitComet 0.87以降用）
#	$msg =~ s/([^=^\"]|^)(bc\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)/$1<a href=\"$2\" target=\"$target\" rel=\"nofollow\">$2<\/a>/g;
# 同一サイト内の旧式の長いURL指定を置換（表示はそのままのつもり）
	$msg =~ s/\"($fullscript\?)mode=view\&amp\;([^\&]*)/\"$1$2/g;
# 同一サイト内のリンクの nofollow 除去
#	$msg =~ s/<a href=\"($fullscript)([\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]*)\" ([^\s]*) rel=\"nofollow\">/<a href=\"$1$2\" $3>/g;
	$msg =~ s/<a href=\"($home)([\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]*)\" (.*) rel=\"nofollow\">/<a href=\"$1$2\" $3>/g;
# もともとの >> リンク処理（同一記事内）
#$msg =~ s/&gt;&gt;([0-9]?[0-9]?[0-9]?)/<a href=\"$readcgi?no=$f&l=1-1000#$1\">&gt;&gt;$1$2<\/a>/gi;
$msg =~ s/&gt;&gt;([0-9]?[0-9]?[0-9]?)/<a href=\"#\" class=\"scroll\" name="\d$1\">&gt;&gt;$1<\/a>/gi;

#	$msg =~ s/&gt;&gt;\[([\d]+)&gt;([\d]+)\]/<a href=\"$readcgi?mode=view2&f=$1&no=$2\" target=\"$target\">&gt;&gt;\[$1&gt;$2\]<\/a>/gi;
# URLを短くしたためコレでOK
#	$msg =~ s/&gt;&gt;(\d)([\d\-]*)/<a href=\"$readcgi?no=$in{'no'}&l=$1$2\" target=\"$target\">&gt;&gt;$1$2<\/a>/gi;

	# スマイル画像変換
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
#  画像リサイズ
#-------------------------------------------------
sub resize {
	local($w,$h) = @_;

	# 引数チェック
	if(int($w) == 0 || int($h) == 0) {
		return (0,0);
	}

	# 画像表示 拡大/縮小
	if ($w != $img_max_w || $h != $img_max_h) {
		# 長辺の拡縮率を計算し、短辺の拡縮率としても使用する
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
#  メールフォーム（ユーザー間）
#-------------------------------------------------
sub mailform {
	if ($ReadOnly) {
		&error("${Oshirase}メールの送信もできません。");
	}

	if (!$usermail) {
		&error("ユーザー間のメール送信機能\は無効になっています。");
	}

	# 報告種別判定
	# 1: コメント報告  2: 違反スレッド報告  3: 警告スレッド報告
	my $type = exists($in{'type'}) ? int($in{'type'}) : 0;
	if ($type < 1 || $type > 3 || ($type == 1 && !exists($in{'no'}))) {
		error("不正なアクセスです");
	}

	# 対象レスNo決定
	my $target_res_no = $in{'type'} == 1 ? int($in{'no'}) : 1;

	# mail.log 制限判定
	## ホストとUserAgentを判定するユーザーであるかどうか(除外対象ではないかどうか)を判定
	my $same_host_ua_judge = 1;
	foreach my $exclude_host (@ngthread_thread_list_creator_name_override_exclude_hosts) {
		if (index($host, $exclude_host) >= 0) {
			$same_host_ua_judge = 0;
			last;
		}
	}
	## mail.log 連続送信制限・同一レス連続報告制限判定
	open(my $maillog_fh, '<', $mailfile) || error("Open Error: $mailfile");
	flock($maillog_fh, 1) || error("Lock Error: $mailfile");
	while (<$maillog_fh>) {
		chomp($_);
		my ($maillog_thread_num, $maillog_res_num, $maillog_host, $maillog_useragent,
			$maillog_cookiea, $maillog_userid, $maillog_history_id, $maillog_time) = split(/<>/, $_);
		# $usermail_time_of_continuously_send_restrictingを経過したログ行は制限判定を行わない
		if ($maillog_time + $usermail_time_of_continuously_send_restricting <= $time) {
			next;
		}

		# 同一ユーザーの場合のみ、制限判定を行う
		if (($same_host_ua_judge && $maillog_host eq $host && $maillog_useragent eq $useragent)
			|| $maillog_cookiea eq $cookie_a
			|| ($maillog_userid ne '-' && $maillog_userid eq $cuser_id)
			|| ($maillog_history_id ne '-' && $maillog_history_id eq $chistory_id)
		) {
			# 制限判定
			# 連続送信制限判定 ($mailwait)
			# 同一レス連続報告制限判定 ($usermail_time_of_continuously_send_restricting)
			if ($maillog_time + $mailwait > $time
				|| ($maillog_thread_num == $in{'f'} && $maillog_res_num == $target_res_no)
			) {
				error("連続送信はもうしばらく時間をおいて下さい");
			}
		}
	}
	close($maillog_fh);

	# スレッドログファイルオープン
	my $thread_logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";
	open(my $threadlog_fh, '<', $thread_logfile_path) || error("Open Error: $in{'f'}.cgi");
	flock($threadlog_fh, 1) || error("Lock Error: $in{'f'}.cgi");

	# スレッドログファイル先頭行を取得し、スレッド名・レス数を取得
	my $top = <$threadlog_fh>;
	chomp($top);
	my ($sub, $num_of_res) = (split(/<>/, $top))[1, 2];
	$sub =~ s/\0*//g;  # スレッド名に含まれているnull文字(\0)を削除
	if ($num_of_res == 0) {
		$num_of_res = 1;
	}

	# コメント報告の場合、存在するレスであるかどうかのチェックを行い、名前・ホスト名・コメントを取得する
	# それ以外の報告の場合は、先頭のレスの名前・ホスト名・コメントを取得する
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
		error("該当するレスが見つかりません");
	}

	# スレッドログファイルクローズ
	close($threadlog_fh);

	# メールフォームに表示する宛先メールアドレス(*で置き換えたもの)
	my $to_eml_asterisk = $usermail_to_address;
	$to_eml_asterisk =~ s/./*/g;

	# クッキー取得
	my ($cnam) = &get_cookie;

	# 報告種別 フォームタイトル・説明文 配列定義
	my @form_contents = (
		undef, # dummy
		["[コメント報告]", "コメント報告です。<br>\nCCCCCC<br>\nCCCCCC\n"],
		["[違反スレッド報告]", "違反スレッド報告です。<br>\nBBBBB<br>\nBBBBB\n"],
		["[警告スレッド報告]", "警告スレッド報告です。<br>\nAAAAA<br>\nAAAAA\n"]
	);

	&header("メール送信フォーム");

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
&nbsp; <b>メールフォーム${$form_contents[$type]}[0]</b></td>
<td align="right" bgcolor="$col3" nowrapper-main>
<a href="javascript:history.back()">前画面に戻る</a></td>
</tr></table></Td></Tr></Table>

${$form_contents[$type]}[1]

<form action="$registcgi" method="post" name="myFORM" id="postform">
<input type="hidden" name="mode" value="mail">
<input type="hidden" name="job" value="send">
<input type="hidden" name="type" value="$type">
<input type="hidden" name="pm">
<input type="hidden" name="f" value="$in{'f'}">
EOM

	# コメント報告時のみレスNoを送信
	if ($type == 1) {
		print "<input type=\"hidden\" name=\"no\" value=\"$target_res_no\">\n";
	}

	print <<"EOM";
<Table border=0 cellspacing=0 cellpadding=0 width="100%">
<Tr><Td bgcolor="$col1">
<table border=0 cellspacing=0 cellpadding=5 width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>宛先</td>
  <td><input type="text" size=30 value="$res_name" maxlength=20 disabled></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>宛先アドレス</td>
  <td><input type="text" size=30 value="$to_eml_asterisk" disabled> （非表\示）
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>件名</td>
  <td><input type="text" size=$sublength value="$sub" maxlength=$sublength disabled></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>差出人</td>
  <td><input type="text" name="name" size=30 value="$cnam" maxlength=20></td>
</tr>
EOM

	# 種類プルダウンメニュー
	if ($type != 3) {
		print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80 nowrapper-main>種類</td>
  <td>
    <select name="category">
  	  <option value="-" selected>-</option>
  	  <option value="個人情報">個人情報</option>
  	  <option value="犯罪予\告">犯罪予\告</option>
  </td>
</tr>
EOM
	}

	# 投稿キー
	if ($regist_key_res) {
		# キー生成
		require $regkeypl;
		my ($str_plain, $str_crypt) = &pcp_makekey;

		# 入力フォーム
		print qq |<tr bgcolor="$col2"><th bgcolor="$col2" width="100">投稿キー(必須)</th>|;
		print qq |<td bgcolor="$col2"><input type="text" name="regikey" size="6" style="ime-mode:inactive">\n|;
		print qq |（投稿時4桁の数字" <img src="$registkeycgi?$str_crypt" align="absmiddle" alt="投稿キー">" を入力してください）<a href="$registkeycgi?$str_crypt" target="_blank">数字が見えない場合こちらをクリック</a></td></tr>\n|;
		print qq |<input type="hidden" name="str_crypt" value="$str_crypt">\n|;
	}

	print <<"EOM";
</select></td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width=80>本文</td>
  <td bgcolor="$col2">
EOM

	$res_comment =~ s/<br>/\r/g;
	print <<"EOM";
元の文章（送信されます）<br>
<textarea cols=$cols rows=$rows wrapper-main=soft disabled>$res_comment</textarea><br>
メール本文（送信されます）<br>
<textarea name=comment cols=$cols rows=$rows wrapper-main=soft></textarea></td></tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="submit" value="メールを送信する"> ※メールは連続して送信できませんのでよく内容を確認してください。</td>
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
#  プレビュー
#-------------------------------------------------
sub preview {
	if ($ReadOnly) {
		&error("$Oshirase");
	}

	# 権限チェック
	if ($authkey && $my_rank < 2) {
		&error("投稿の権限がありません");
	}

	# ヘッダ
	if ($smile) { &header("新規スレッド作成プレビュー", "js"); }
	else { &header("新規スレッド作成プレビュー"); }

	print <<"EOM";
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%">
<tr>
  <td align="left" nowrapper-main>
	<a href="$bbscgi?">トップページ</a> &gt; 新規スレッド作成（プレビュー）
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>内容を確認してタイトルを設定してください</b></td>
</tr></table></Td></Tr></Table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td>
<font color="$col4"><br>
EOM

# プレチェック
	# コメント文字数チェック
	if (length($i_com) > $max_msg*2) {
		print "文字数オーバーです。<br>全角$max_msg文字以内で記述してください<br>\n";
	}

	# 汚染チェック
	$in{'res'} =~ s/\D//g;

	# 投稿内容チェック
	if ($i_com eq "") { print "コメントの内容がありません<br>\n"; }
	if ($i_nam eq "") {
		if ($in_name) { print "名前は記入必須です<br>\n"; }
		else { $i_nam = '名無し'; }
	}
	if ($in_mail == 1 && $in{'email'} eq "") { print "E-mailは記入必須です<br>\n"; }
	if ($in_mail == 2 && $in{'email'} ne "") { print "E-mailは入力禁止です<br>\n"; }
	if ($in_mail == 3 && $in{'email'} ne "") { print "E-mailは入力禁止です<br>\n"; }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		print "E-mailの入力内容が不正です<br>\n";
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { print "名前は正しく記入してください<br>\n"; }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { print "コメントは正しく記入してください<br>\n"; }
	if ($in_pwd && $in{'pwd'} eq "") { print "パスワードは入力必須です<br>\n"; }
	if (length($in{'pwd'}) > 8) { print "パスワードは8文字以内にして下さい<br>\n"; }
	if ($webprotect_auth_new && $in{'user_id'} eq "") { print "登録IDは入力必須です<br>\n"; }
	if ($webprotect_auth_new && $in{'user_pwd'} eq "") { print "登録パスワードは入力必須です<br>\n"; }

	# 投稿キーチェック
	if ($regist_key_new) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			print "投稿キーが入力不備です。示されている数字を入力してください<br>\n";
		}

		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
	}

	print <<"EOM";
</font>
</Td></Tr></Table>
EOM

	&form2("preview");

	print "</div><!-- 終了 container --></body></html>\n";
	exit;
}

#-------------------------------------------------
#  プレビュー（レス用）
#-------------------------------------------------
sub resview {

	# ヘッダ
	if ($smile) { &header("返信プレビュー", "js"); }
	else { &header("返信プレビュー"); }

	print <<"EOM";
<div id="container">
<div id="wrapper-main">
<div id="wrapper-main-in">
<table width="100%">
<tr>
  <td align="left" nowrapper-main>
	<a href="$bbscgi?">トップページ</a> &gt; <a href=\"$readcgi?no=$in{'res'}\">スレに戻る</a> &gt; 返信（プレビュー）
  </td>
</tr></table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="15" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrapper-main width="92%">
<img src="$imgurl/pen.gif" align="middle">
&nbsp; <b>内容を確認してタイトルを設定してください</b></td>
</tr></table></Td></Tr></Table>
<Table border="0" cellspacing="0" cellpadding="0" width="100%">
<Tr><Td>
<font color="$col4"><br>
EOM

# プレチェック
	# コメント文字数チェック
	if (length($i_com) > $max_msg*2) {
		print "文字数オーバーです。<br>全角$max_msg文字以内で記述してください<br>\n";
	}

	# 汚染チェック
	$in{'res'} =~ s/\D//g;

	# スレッドログを先頭2行読み込み
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

	# スレッドタイトル読み込み
	my $sub = ${$log[0]}[1];
	$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

	# 親レス読み込み
	my ($ho,$url,$user_id,$cookie_a,$history_id) = @{$log[1]}[6,8,16,18,19];

	# スレッドタイトルによる書き込み制限機能のスレッド作成者の除外機能
	# >>1の ホスト, URL欄, 登録ID, CookieA, 書込ID を取得
	my %first_res = (
		'host'       => $ho,
		'url'        => $url,
		'user_id'    => $user_id,
		'cookie_a'   => $cookie_a,
		'history_id' => $history_id,
	);

	# 投稿内容チェック
	if ($i_com eq "") { print "コメントの内容がありません<br>\n"; }
	if ($i_nam eq "") {
		if ($in_name) { print "名前は記入必須です<br>\n"; }
		else { $i_nam = '名無し'; }
	}
	if ($in_mail == 1 && $in{'email'} eq "") { print "E-mailは記入必須です<br>\n"; }
	if ($in_mail == 2 && $in{'email'} ne "") { print "E-mailは入力禁止です<br>\n"; }
	if ($in_mail == 3 && $in{'email'} ne "") { print "E-mailは入力禁止です<br>\n"; }
	if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		print "E-mailの入力内容が不正です<br>\n";
	}
	if ($i_nam =~ /^(\x81\x40|\s)+$/) { print "名前は正しく記入してください<br>\n"; }
	if ($i_com =~ /^(\x81\x40|\s|<br>)+$/) { print "コメントは正しく記入してください<br>\n"; }
	if ($in_pwd && $in{'pwd'} eq "") { print "パスワードは入力必須です<br>\n"; }
	if (length($in{'pwd'}) > 8) { print "パスワードは8文字以内にして下さい<br>\n"; }
	if ($webprotect_auth_res && $in{'user_id'} eq "") { print "登録IDは入力必須です<br>\n"; }
	if ($webprotect_auth_res && $in{'user_pwd'} eq "") { print "登録パスワードは入力必須です<br>\n"; }

	# 投稿キーチェック
	if ($regist_key_res) {
		require $regkeypl;

		if ($in{'regikey'} !~ /^\d{4}$/) {
			print "投稿キーが入力不備です。示されている数字を入力してください<br>\n";
		}

		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
	}

	print <<"EOM";
</font>
</Td></Tr></Table>
EOM

	&form2("resview", $sub, \%first_res);

	print "</div><!-- 終了 container --></body></html>\n";

	exit;
}

# NGネーム機能利用時のNGレス投稿者名表示カット機能で使用します
# 表示部分・カット部分をそれぞれ分けてリストとして返します
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

# NGワード機能のCookieセットで使用します
sub set_ngword_cookie {
	# 改行コードをLFで統一
	$in{'ngwords'} =~ s/\r\n/\n/g;
	$in{'ngwords'} =~ s/\r/\n/g;

	# 文字実体参照をデコード
	$in{'ngwords'} = HTML::Entities::decode($in{'ngwords'});

	# UTF8フラグ付き文字に変換後、LFでsplitし、空行の要素を削除
	my @ngwords = grep { $_ ne '' } split(/\n/, $enc_cp932->decode($in{'ngwords'}));

	if (defined($chistory_id)) {
		# 書込IDに保存
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngword_settings(\@ngwords);
		$history_log->DESTROY();
	} else {
		# Cookie名決定
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGWORD_LIST";

		# 要素数が1つ以上ある場合はセットし、そうでない場合はCookieを削除
		if (scalar(@ngwords) > 0) {
			# JSON形式に変換後、URLエンコード
			my $urlencoded_json_ngwords = JSON::XS->new->utf8(1)->encode(\@ngwords);
			$urlencoded_json_ngwords =~ s/(\W)/'%' . unpack('H2', $1)/eg;
			$urlencoded_json_ngwords =~ s/\s/+/g;

			# Cookieサイズ判定
			if(length($cookie_name . $urlencoded_json_ngwords) > 4093) {
				error("文字数オーバーです。");
			}

			# Cookieセット
			print "Set-Cookie: $cookie_name=$urlencoded_json_ngwords; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
		} else {
			# Cookie削除
			print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
		}
	}

	# 成功メッセージ表示
	success("NGワード設定しました。");
}

# 連鎖NG機能のCookieセットで使用します
sub set_chain_ng {
	# 連鎖NG機能 フラグ取得
	my $flg = $chain_ng; # デフォルト値を予め取得
	if(exists($in{'chainng'}) && ($in{'chainng'} eq "0" || $in{'chainng'} eq "1")) {
		$flg = $in{'chainng'};
	}

	if (defined($chistory_id)) {
		# 書込IDに保存
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_chain_ng_setting($flg);
		$history_log->DESTROY();
	} else {
		# Cookieセット
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_CHAIN_NG";
		print "Set-Cookie: $cookie_name=$flg; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
	}

	# 成功メッセージ表示
	success("連鎖を" . ($flg ? "有効" : "無効") . "に設定しました。");
}

# 自分の投稿を目立たせる機能の設定取得で使用します
sub get_highlight_name_on_own_post {
	my $ret_val = 1; # 未設定時は有効
	if (defined($chistory_id)) {
		# 書込IDログから取得
		my $instance = HistoryLog->new($chistory_id);
		if ((my $flg = $instance->get_highlight_name_active_flag()) >= 0) {
			# 書込IDログに保存されている時はそのフラグを取得
			$ret_val = $flg;
		}
		$instance->DESTROY();
	} else {
		# Cookieから取得
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_HIGHLIGHT_NAME";
		foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
			my ($name, $value) = split(/=/, $cookie_set);
			if ($name eq $cookie_name) {
				# Cookieに保存されているときはその値を確かめた上でフラグを取得
				if ($value eq '1' || $value eq '0') {
					$ret_val = int($value);
				}
				last;
			}
		}
	}
	return $ret_val;
}

# 自分の投稿を目立たせる機能の設定で使用します
sub set_highlight_name_on_own_post {
	# フラグ取得
	my $flg = 1;
	if(exists($in{'highlightname'}) && ($in{'highlightname'} eq "0" || $in{'highlightname'} eq "1")) {
		$flg = int($in{'highlightname'});
	} else {
		error("自分の投稿を目立たせるを設定できませんでした。");
	}

	if (defined($chistory_id)) {
		# 書込IDに保存
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_highlight_name_active_flag($flg);
		$history_log->DESTROY();
	} else {
		# Cookieセット
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_HIGHLIGHT_NAME";
		print "Set-Cookie: $cookie_name=$flg; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
	}

	# 成功メッセージ表示
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
	success("目立たせるを" . ($flg ? "有効" : "無効") . "に設定しました。", $back_url);
}

# 登録したNGネームの一括削除で使用します
sub clear_ngname {
	if (defined($chistory_id)) {
		# 書込IDに保存
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngname_settings();
		$history_log->DESTROY();
	} else {
		# Cookie削除
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGNAME_LIST";
		print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
	}

	# 成功メッセージ表示
	success("登録したNGネームを全て削除しました。");
}

# 登録したNGIDの一括削除で使用します
sub clear_ngid {
	if (defined($chistory_id)) {
		# 書込IDに保存
		my $history_log = HistoryLog->new($chistory_id);
		$history_log->set_ngid_settings();
		$history_log->DESTROY();
	} else {
		# Cookie削除
		my $cookie_name = "WEB_PATIO_${cookie_current_dirpath}_NGID_LIST";
		print "Set-Cookie: $cookie_name=; expires=Thu, 1 Jan 1970 00:00:00 GMT\n";
	}

	# 成功メッセージ表示
	success("登録したNGIDを全て削除しました。");
}

# 表示内容分岐機能の分岐判定
sub judge_branch_contents {
	# 引数がログ行をカラムで分割した配列リファレンス、
	# もしくは、スカラー変数であるかどうか
	my ($subject_or_reslogArrayRef) = @_;
	my $is_res_log_array_reference = ref($subject_or_reslogArrayRef) eq 'ARRAY';
	if ($is_branching_contents || (!$is_res_log_array_reference && ref($subject_or_reslogArrayRef) ne '')) {
		return;
	}
	# 表示内容分岐機能 文字列一致判定
	my @decoded_targets = do {
		if ($is_res_log_array_reference) {
			# ログ行をカラムで分割した配列リファレンス
			# ${$subject_or_reslogArrayRef}[2] -> 名前  ${$subject_or_reslogArrayRef}[4] -> レス内容
			($enc_cp932->decode(${$subject_or_reslogArrayRef}[2]), $enc_cp932->decode(${$subject_or_reslogArrayRef}[4]));
		} else {
			# スレッドタイトル
			($enc_cp932->decode($subject_or_reslogArrayRef));
		}
	};
	foreach my $decoded_keyword (@decoded_contents_branching_keyword) {
		# 設定した文字列を含んでいるかどうか
		foreach my $decoded_target (@decoded_targets) {
			if (index($decoded_target, $decoded_keyword) > -1) {
				$is_branching_contents = 1;
				return;
			}
		}
	}

	# 表示内容分岐機能 画像を含んでいるかどうか (引数がスレッドタイトルの時は判定を行わない)
	if ($is_res_log_array_reference && $contents_branching_img_check
			&& ((split(/,/, ${$subject_or_reslogArrayRef}[12]))[0] ne ''
				|| (split(/,/, ${$subject_or_reslogArrayRef}[13]))[0] ne ''
				|| (split(/,/, ${$subject_or_reslogArrayRef}[14]))[0] ne ''
				)
		) {
		$is_branching_contents = 1;
	}
}

# スレッド画面からユーザーを制限する機能 HTML作成
sub create_restrict_user_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# aタグの属性値を作成
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

	# HTMLを作成し、返す
	return <<"EOC";
EOC
}

# スレッド画面からユーザーを時間制限する機能 HTML作成
sub create_restrict_user_by_time_range_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# aタグの属性値を作成
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

	# HTMLを作成し、返す
	return <<"EOC";
EOC
}

# スレッド画面からユーザーを制限する機能 (そのスレのみ) HTML作成
sub create_in_thread_only_restrict_user_link_html {
	my ($cookie_a, $history_id, $host, $user_id) = @_;

	# aタグの属性値を作成
	my $a_attr_html = '';
	foreach my $target_pair_ref (['cookie_a', $cookie_a], ['history_id', $history_id], ['host', $host], ['user_id', $user_id]) {
		my ($name, $value) = @{$target_pair_ref};
		if (!defined($value) || $value eq '') {
			next;
		}
		$a_attr_html .= " $name=\"$value\"";
	}
	if ($a_attr_html ne '') {
		# 先頭にスレッドNoを付加
		$a_attr_html = ' thread_num="' . int($in{'no'}) . '"' . $a_attr_html;
	} else {
		return '';
	}

	# HTMLを作成し、返す
	return <<"EOC";
EOC
}

# ユーザー強調表示機能 登録・削除フォームHTML作成
sub create_highlight_userinfo_form_html {
    my ($res_cookie_a, $res_history_id, $res_host, $res_user_id) = @_;

    # 登録ボタン・削除リンク共通で追加する、ユーザー情報属性を作成
    my $userinfo_attr = '';
    foreach my $target_pair_ref (['cookie_a', $res_cookie_a], ['history_id', $res_history_id], ['host', $res_host], ['user_id', $res_user_id]) {
        my ($name, $value) = @{$target_pair_ref};
        if (!defined($value) || $value eq '') {
            next;
        }
        $userinfo_attr .= " $name=\"$value\"";
    }

#    # selectタグ・色候補のoptionタグを作成
#    my $select_option_html = "<select class=\"highlight_userinfo_color\">\n";
#    for (my $i = 0; $i < scalar(@highlight_userinfo_color_name_code); $i++) {
#        my $color_number = $i + 1;
#        $select_option_html .= "\t<option value=\"$color_number\">値$color_number：${$highlight_userinfo_color_name_code[$i]}[0]</option>\n";
#    }
#    $select_option_html .= "</select>";

    # HTMLを作成し、返す
#    return <<"EOC";
#$select_option_html
#<button type="button" class="highlight_userinfo_add"$userinfo_attr>登録</button>
#<span class="highlight_userinfo_ajax_message highlight_userinfo_add_ajax_message"></span>
#&nbsp;&nbsp;
#<a href="#" class="highlight_userinfo_remove"$userinfo_attr>削除</a>
#<span class="highlight_userinfo_ajax_message highlight_userinfo_remove_ajax_message"></span>
#EOC
}

1;
