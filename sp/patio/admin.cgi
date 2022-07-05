#!/usr/bin/perl

#┌─────────────────────────────────
#│ [ WebPatio ]
#│ admin.cgi - 2007/05/06
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# きりしま式 K1.04
# 2013/03/03 過去ログのバグ修正
# 2009/07/04 最後のレスを削除するときの不具合
# 2009/07/03 過去ログに落とすときにスレッド一覧のフラグを直していなかった
# 2009/06/26 過去ログのスレッド操作に「開閉・管理者・ＦＡＱ」があるのは変なので出なくした
# 2009/03/18 FAQモードに挑戦
# 2009/03/14 スレッド作成制限モードの追加
# 2008/08/29 いったん一式アーカイブを更新
# 2008/03/16 分割処理のバグ修正
# 2008/02/27 スレッド分割機能を装備（厳密には指定レス以降をコピーして新規スレッド作成）
# 2008/01/09 過去ログ化<->復元の際に各スレッドのログに状態を記録するように変更
# 2007/11/14 過去ログ化<->復元
# 2007/06/23 ロックを管理者ロックに、ロック時にレスのタイトルを失わないように
# 2007/06/10 3.2相当に修正

# 外部ファイル取り込み
require './init.cgi';
require $jcode;
use lib qw(./lib ./lib/perl5 ./protect_rireki/lib);
use File::Basename;
use File::Copy;
use File::Find::Rule;
use File::Spec;
use ThreadUpdateLogDB;

use HistoryCookie;

&parse_form;
if($in{'cookie_id'} eq 'on'){
	my $cookie = HistoryCookie->new();
	if (!defined($cookie->('HISTORY_ID'))) {
		# 未ログイン時に、書込ID発行/書込ID認証フォーム表示
		if($in{'pass'} ne $pass){
			&error("認証エラー");
		}
	} else {
		my $history_id = $cookie->('HISTORY_ID');
		if(!( grep $_ eq $history_id , @setteiti)){
			&error("認証エラー");
		}
	}
} else{
	if ($in{'pass'} eq "") { &enter; }
	elsif ($in{'pass'} ne $pass) { &error("認証エラー"); }
}
if ($in{'logfile'} || $in{'bakfile'}) { &file_mente; }
elsif ($in{'filesize'}) { &filesize; }
elsif ($in{'member'} && $authkey) { &member_mente; }
elsif ($in{'config_override_settings'}) { &config_override_settings; }
elsif ($in{'rebuild_thread_updatelog_db'}) { &rebuild_thread_updatelog_db; }
elsif ($in{'move_threadlog'}) { move_threadlog(); }
elsif ($in{'action'} && $in{'file'}) { manage_log(); }
&menu_disp;

#-------------------------------------------------
#  ログメンテ
#-------------------------------------------------
sub file_mente {
	local($subject,$log,$top,$itop,$sub,$res,$nam,$em,$com,$da,$ho,$pw,$re,
		$sb,$na2,$key,$last_nam,$last_dat,$del,@new,@new2,@sort,@file,@del,@top);

	# メニューからの処理
	if ($in{'job'} eq "menu") {
		foreach ( keys(%in) ) {
			if (/^past(\d+)/) {
				$in{'past'} = $1;
				last;
			}
		}
	}

	# 汚染チェック
	$in{'no'} =~ s/[^0-9\0]//g;

	# index定義
	local($mylog);
	if ($in{'bakfile'}) {
		$log = $pastfile;
		$subject = "過去ログ";
		$mylog = "bakfile";
	} else {
		$log = $nowfile;
		$subject = "現行ログ";
		$mylog = "logfile";
	}

	# スレッド一括削除
	if ($in{'action'} eq "del" && $in{'no'} ne "") {

		# 削除情報
		local(@del) = split(/\0/, $in{'no'});

		# スレッド更新日時管理データベース接続
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);

		# indexより削除情報抽出
		local($top, @new);
		open(DAT,"+< $log") || &error("Open Error: $log");
		eval "flock(DAT, 2);";
		$top = <DAT> if (!$in{'bakfile'});
		while(<DAT>) {
			$flg = 0;
			local($no) = split(/<>/);
			foreach $del (@del) {
				if ($del == $no) {
					# ログ展開
					my $logfile_path = get_logfolder_path($del) . "/$del.cgi";
					open(DB, $logfile_path);
					while(my $db = <DB>) {
						$db =~ s/(?:\r\n|\r|\n)$//;
						my ($tim, %upl);
						($tim,$upl{1},$upl{2},$upl{3},$upl{4},$upl{5},$upl{6}) = (split(/<>/, $db))[11 .. 14, 23 .. 25];

						# 画像削除
						foreach my $i (1 .. 6) {
							my ($img_folder_number, $ex) = split(/,/, $upl{$i});

							if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
								unlink("$upldir/$img_folder_number/$tim-$i$ex");
							}
							# サムネイル画像ファイルが存在したら削除
							if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
								unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
							}
						}
					}
					close(DB);

					# スレッド削除
					unlink($logfile_path);

					# スレッド更新日時管理データベースから、削除されたスレッド情報を削除
					$updatelog_db->delete_threadinfo($del);

					$flg = 1;
					last;
				}
			}
			if (!$flg) { push(@new,$_); }
		}

		# index更新
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

		# スレッド更新日時管理データベース切断
		$updatelog_db->close(0);

	# スレッドのロック開閉
	} elsif ($in{'action'} eq "lock" && $in{'no'} ne "" && !$in{'past'}) {

		# ロック情報
		local(@lock) = split(/\0/, $in{'no'});

		# スレッドヘッダ情報更新
		foreach (@lock) {

			local($top,@file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# 先頭記事分解、キー開閉
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=ロック 1=標準 2=管理用
#			if ($key eq '0') { $key = 1; } else { $key = 0; }
			# 管理者ロック
			if ($key eq '4') { $key = 1; } else { $key = 4; }

			# スレッド更新
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index読み込み
		local($top,@new);
		open(DAT,"+< $log") || &error("Open Error: $log");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			chomp($_);
			local($no,$sub,$res,$nam,$da,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp ($ressub);
			chomp ($restime);

			foreach $lock (@lock) {
				# 0=ロック 1=標準 2=管理用
				if ($lock == $no) {
				#  indexの状態に関係なく、個別ログのロック状態に合わせる

				my $logfile_path = get_logfolder_path($lock) . "/$lock.cgi";
				open(IND, "+<", $logfile_path) || &error("Open Error: $lock.cgi");
				eval "flock(IND, 2);";
				$top2 = <IND>;
				close(IND);

				# 先頭記事分解、キー開閉
				local(undef,undef,undef,$key2) = split(/<>/, $top2);

#					if ($key eq '0') { $key = 1; } else { $key = 0; }
					$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key2<>$upl<>$ressub<>$restime<>$host<>";
				}
			}
			push(@new,"$_\n");
		}

		# index更新
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# スレッドの管理者コメントモード
	} elsif ($in{'action'} eq "lock2" && $in{'no'} ne "" && !$in{'past'}) {

		# ロック情報
		local(@lock) = split(/\0/, $in{'no'});

		# スレッドヘッダ情報更新
		foreach (@lock) {

			local($top, @file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# 先頭記事分解、キー開閉
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=ロック 1=標準 2=管理用
			if ($key != 2) { $key = 2; } else { $key = 1; }

			# スレッド更新
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index読み込み
		local($top, $flg, @new, @top1, @top2, @faq);
		open(DAT,"+< $log") || &error("Open Error: $log");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			$flg = 0;
			chomp($_);
			local($no,$sub,$res,$nam,$da,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp ($ressub);
			chomp ($restime);

			foreach $lock (@lock) {
				if ($lock == $no) {
					# 0=ロック 1=標準 2=管理用
					if ($key == 2) {
						$key = 1;
						$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>$host<>";
					} else {
						$key = 2;
						push(@top1,"$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>$host<>\n");
						$flg = 1;
					}
					last;
				}
			}
			if (!$flg) {
				if ($key == 2) {
					push(@top2,"$_\n");
				} elsif ($key == 3){
					push(@faq,"$_\n");
				} else {
					push(@new,"$_\n");
				}
			}
		}

		# index更新
		unshift(@new,@faq) if (@faq > 0);
		unshift(@new,@top2) if (@top2 > 0);
		unshift(@new,@top1) if (@top1 > 0);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# スレッドのＦＡＱモード 管理者コメントモードのパクリ
#	} elsif ($in{'action'} eq "lock2" && $in{'no'} ne "" && !$in{'past'}) {
	} elsif ($in{'action'} eq "faq" && $in{'no'} ne "" && !$in{'past'}) {

		# ロック情報
		local(@lock) = split(/\0/, $in{'no'});

		# スレッドヘッダ情報更新
		foreach (@lock) {

			local($top, @file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# 先頭記事分解、キー開閉
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=ロック 1=標準 2=管理用 3=ＦＡＱ
			if ($key != 3) { $key = 3; } else { $key = 1; }

			# スレッド更新
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index読み込み
		local($top, $flg, @new, @top1, @top2 ,@faq);
		open(DAT,"+< $log") || &error("Open Error: $log");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			$flg = 0;
			chomp($_);
			local($no,$sub,$res,$nam,$da,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp ($ressub);
			chomp ($restime);

			foreach $lock (@lock) {
				if ($lock == $no) {
					# 0=ロック 1=標準 2=管理用 3=ＦＡＱ
					if ($key == 3) {
						$key = 1;
						$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>$host<>";
					} else {
						$key = 3;
						push(@faq,"$no<>$sub<>$res<>$nam<>$da<>$na2<>$key<>$upl<>$ressub<>$restime<>$host<>\n");
						$flg = 1;
					}
					last;
				}
			}
			if (!$flg) {
				if ($key == 2) {
					push(@top2,"$_\n");
				} elsif ($key == 3){
					push(@faq,"$_\n");
				} else {
					push(@new,"$_\n");
				}
			}
		}

		# index更新
		unshift(@new,@faq) if (@faq > 0);
		unshift(@new,@top2) if (@top2 > 0);
		unshift(@new,@top1) if (@top1 > 0);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# スレッドの過去ログ化 regist.cgi の新規書き込みルーチンをパクリ
	} elsif ($in{'action'} eq "archive" && $in{'no'} ne "" && $in{'logfile'}) {

	# 選択スレッド情報展開
	local(@lock) = split(/\0/, $in{'no'});

		# index読み込み
#	local($i, $flg, $top, @new, @tmp, @top);

		local($flg,$top,@now,@past);
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			$flg = 0;
#			chomp($_);
			local($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp($host); # スレッド作成者ホスト名が記録されていない旧フォーマットのログでは\nが入るため、互換用

			foreach $lock (@lock) {
				if ($lock == $num) {
				$flg = 1;
				last;
				}
			}
			if ($flg) {
#			unshift(@past,$_);
#			push(@past,$_);
#			オリジナル形式のログ対応
			chomp ($upl);
			chomp ($ressub);
			chomp ($restime);
			push(@past,"$num<>$sub<>$res<>$nam<>$date<>$na2<>-1<>$upl<>$ressub<>$restime<>$host<>\n");

			# 過去ログに落ちるスレッドのフラグを変更

		# スレッド読み込み
		my $logfile_path = get_logfolder_path($num) . "/$num.cgi";
		open(DAT2, "+<", $logfile_path) || &error("Open Error: $num.cgi");
		eval "flock(DAT2, 2);";
		local(@file) = <DAT2>;

		# 先頭ファイルを抽出・分解
		$top2 = shift(@file);
		local($no,$sub2,$res2,undef) = split(/<>/, $top2);

		# フラグ変更・スレッド更新
		unshift(@file,"$no<>$sub2<>$res2<>-1<>\n");

		seek(DAT2, 0, 0);
		print DAT2 @file;
		truncate(DAT2, tell(DAT2));
		close(DAT2);

		# スレッド更新日時管理データベースに、過去ログに落ちるスレッド情報を更新
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($num, undef, 0);
		$updatelog_db->close(0);

			} else {
			push(@now,$_);
			}
		}

		# index更新
		unshift(@now,$top);
		seek(DAT, 0, 0);
		print DAT @now;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 過去index更新
		if (@past > 0) {
#			$i = @tmp;
			open(DAT,"+< $pastfile") || &error("Open Error: $pastfile");
			eval "flock(DAT, 2);";
			while(<DAT>) {
				push(@past,$_);
			}
			seek(DAT, 0, 0);
			print DAT @past;
			truncate(DAT, tell(DAT));
			close(DAT);
		}


	# 過去ログの復帰 regist.cgi の新規書き込みルーチンをパクリ
	} elsif ($in{'action'} eq "extract" && $in{'no'} ne "" && $in{'bakfile'}) {

	# 選択スレッド情報展開
	local(@lock) = split(/\0/, $in{'no'});

		# index読み込み
#	local($i, $flg, $top, @new, @tmp, @top);

		local($flg,$top,@now,@past,@tmp);
#		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
			open(DAT,"+< $pastfile") || &error("Open Error: $pastfile");
		eval "flock(DAT, 2);";
#		$top = <DAT>;
		while(<DAT>) {
			$flg = 0;
#			chomp($_);
			local($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp($host); # スレッド作成者ホスト名が記録されていない旧フォーマットのログでは\nが入るため、互換用

			foreach $lock (@lock) {
				if ($lock == $num) {
				$flg = 1;
				last;
				}
			}
			if ($flg) {
#			unshift(@now,$_);
#			push(@now,$_);
			push(@now,"$num<>$sub<>$res<>$nam<>$date<>$na2<>1<>$upl<>$ressub<>$restime<>$host<>\n");

			# 現行ログに戻るスレッドのフラグを変更

		# スレッド読み込み
		my $logfile_path = get_logfolder_path($num) . "/$num.cgi";
		open(DAT2, "+<", $logfile_path) || &error("Open Error: $num.cgi");
		eval "flock(DAT2, 2);";
		local(@file) = <DAT2>;

		# 先頭ファイルを抽出・分解
		$top2 = shift(@file);
		local($no,$sub2,$res2,undef) = split(/<>/, $top2);

		# フラグ変更・スレッド更新
		unshift(@file,"$no<>$sub2<>$res2<>1<>\n");

		seek(DAT2, 0, 0);
		print DAT2 @file;
		truncate(DAT2, tell(DAT2));
		close(DAT2);

		# スレッド更新日時管理データベースに、現行ログに復帰するスレッド情報を更新
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($num, undef, 1);
		$updatelog_db->close(0);

			} else {
			push(@past,$_);
			}
		}

		# 過去index更新
#		unshift(@now,$top);
		seek(DAT, 0, 0);
		print DAT @past;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 現行index更新
		if (@now > 0) {
		local (@faq);
#			$i = @tmp;
#			open(DAT,"+< $pastfile") || &error("Open Error: $pastfile");
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
			eval "flock(DAT, 2);";
		$top = <DAT>;
			while(<DAT>) {
				local($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
					# 0=ロック 1=標準 2=管理用 3=FAQ
					if ($key == 2) {
					push(@tmp,$_);
					} elsif ($key == 3) {
					push(@faq,$_);
					} else {
					push(@now,$_);
					}
			}
		unshift(@tmp,$top);
			seek(DAT, 0, 0);
			print DAT @tmp;
			print DAT @faq;
			print DAT @now;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

	# スレッド内レス記事閲覧
	} elsif ($in{'action'} eq "view" && $in{'no'} ne "") {

		# レス記事個別削除
		if ($in{'job'} eq "del" && $in{'no2'} ne "") {
			# 削除情報を配列化
			my @del = split(/\0/, $in{'no2'});

			# スレッド内より削除記事を抽出
			my $logfile_path = get_logfolder_path($in{'no'}) . "/$in{'no'}.cgi";
			open(DAT, "+<", $logfile_path);
			eval "flock(DAT, 2);";
			my $top = <DAT>;
			my ($res) = (split(/<>/, $top))[2];

			# スレッドログ2行目(親レス)よりレス番号を取得し、削除可能かどうか判定
			my $parentResNo = (split(/<>/, <DAT>))[0];
			if ($in{'no2'} =~ /^$parentResNo$/) {
				close(DAT);
				&error("親記事の削除はできません");
			}
			seek(DAT, 0, 0);
			<DAT>;

			my (@new, $last_nam,$last_dat,$last_sub,$last_tim);
			my $res_cnt = 0; # 最終レス情報決定用レス数カウンタ (ログに記録するレス数は$resをそのまま使用)
			LOG_LOOP: while(<DAT>) {
				$_ =~ s/(?:\r\n|\r|\n)$//;

				my ($no,$sub,$nam,$da,$tim,%upl);
				($no,$sub,$nam,$da,$tim,$upl{1},$upl{2},$upl{3},$upl{4},$upl{5},$upl{6}) = (split(/<>/, $_))[0 .. 2, 5, 11 .. 14, 23 .. 25];

				# 削除対象レスの場合は画像を削除してスキップ
				foreach my $del (@del) {
					if ($no == $del) {
						# 画像削除
						foreach my $i (1 .. 6) {
							my ($img_folder_number, $ex) = split(/,/, $upl{$i});

							if (-f "$upldir/$img_folder_number/$tim-$i$ex") {
								unlink("$upldir/$img_folder_number/$tim-$i$ex");
							}
							# サムネイル画像ファイルが存在したら削除
							if (-f "$thumbdir/$img_folder_number/$tim-${i}_s.jpg") {
								unlink("$thumbdir/$img_folder_number/$tim-${i}_s.jpg");
							}
						}
						next LOG_LOOP;
					}
				}

				# レス配列に追加
				push(@new, "$_\n");

				# スレッド内で一番最後に更新された記事の時刻を覚える
				if ($tim ne 0 && $tim > $last_tim) { $last_tim = $tim; }

				# 最終投稿者名と時間を覚えておく
				$last_nam = $nam;
				$last_dat = $da;
				# タイトルも
				$last_sub = $sub;
#				$last_tim = $tim;

				$res_cnt++;
			}

			$res_cnt--; # レスカウントから親レスを除く
			if ($res_cnt == 0) {
				# 最終的にレスがない場合
#				$last_nam = "";
#				$last_dat = "";
				$last_sub = "";
#				$last_tim = "";
			}

			# スレッド更新
			unshift(@new,$top);
			seek(DAT, 0, 0);
			print DAT @new;
			truncate(DAT, tell(DAT));
			close(DAT);

			# index内容差し替え
			my (@new2, @sort, @top, @faq);
			open(DAT,"+< $log");
			eval "flock(DAT, 2);";
			my $top2 = <DAT> if ($in{'past'} == 0);
			while(<DAT>) {
				chomp($_);
				my ($no,$sb,$re,$na,$da,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);

				if ($key == 2) {
					push(@top,"$_\n");
					next;
				}
				if ($key == 3 && $in{'no'} != $no) {
					push(@faq,"$_\n");
					next;
				}
				if ($key == 3 && $in{'no'} == $no) {
					# レス個数と最終投稿者名を差替
					$na2 = $last_nam;
					$da  = $last_dat;
					$_ = "$no<>$sb<>$res<>$na<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>$host<>";
					push(@faq,"$_\n");
					next;
				}
				if ($in{'no'} == $no) {
					# レス個数と最終投稿者名を差替
					$na2 = $last_nam;
					$da  = $last_dat;
					$_ = "$no<>$sb<>$res<>$na<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>$host<>";
				}
				push(@new2,"$_\n");

				# ソート用配列
				$da =~ s/\D//g;
				push(@sort,$da);
			}

			# 投稿順にソート
			@new2 = @new2[sort {$sort[$b] <=> $sort[$a]} 0 .. $#sort];

			# index更新
			unshift(@new2,@faq) if (@faq > 0);
			unshift(@new2,@top) if (@top > 0);
			unshift(@new2,$top2) if ($in{'past'} == 0);
			seek(DAT, 0, 0);
			print DAT @new2;
			truncate(DAT, tell(DAT));
			close(DAT);

			# スレッド更新日時管理データベースに、レス削除後のスレッド情報に更新
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$updatelog_db->update_threadinfo($in{'no'}, $last_tim, undef);
			$updatelog_db->close(0);

		# レス記事個別修正
		} elsif ($in{'job'} eq "edit" && $in{'no2'} ne "") {

			# 複数選択の場合は先頭のみ
			($in{'no2'}) = split(/\0/, $in{'no2'});

			require $editlog;
			&edit_log("admin");

		# スレッド分割
		} elsif ($in{'job'} eq "split" && $in{'no2'} ne "") {

			# 厳密には指定したレス以降で新しいスレッドを作る。
			# 元のスレッドはそのままなので、そちらはそちらで削除・編集等をする前提

			local($tops,$num,$res,$key,$i_nam2,$i_tim,$i_da,$i_ho,$flg);
			my @newt;

			# 複数選択の場合は先頭のみ利用
			($in{'no2'}) = split(/\0/, $in{'no2'});

			# スレッド内より削除記事を抽出
#			local($top, @new);
			my $logfile_path = get_logfolder_path($in{'no'}) . "/$in{'no'}.cgi";
			open(DAT, "+<", $logfile_path);
			eval "flock(DAT, 2);";
			$tops = <DAT>;
			local($num,$sub2,undef,undef) = split(/<>/, $tops);
			$res = 1;
			$flg = 0;
			while(<DAT>) {
				$_ =~ s/(?:\r\n|\r|\n)$//;
				local($reno,$sub,$nam,$em,$com,$da,$ho,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$idcrypt,$user_id,$is_sage,
					$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl{4},$upl{5},$upl{6}) = split(/<>/);
				if ($flg) {$res++;}
				if ($reno==$in{'no2'}) {
					# 分割後のスレッドの作成者名をキープ
					$i_nam2 = $nam;
					$i_tim = $tim;
					$i_da= $da;
					$i_ho = $ho;
					$flg=1;
				}
				if ($flg) {
					if ($res == 1) {
						# スレッド分割後に親レスとなるレスの場合
						$sub = $sub2; # スレッドタイトルをレスタイトルとする
						$is_sage = undef; # sageフラグを削除する
					}
					push(@newt, join('<>',
							$res,
							$sub,
							$nam,
							$em,
							$com,
							$da,
							$ho,
							$pw,
							$url,
							$mvw,
							$myid,
							$tim,
							$upl{1},
							$upl{2},
							$upl{3},
							$idcrypt,
							$user_id,
							$is_sage,
							$cookie_a,
							$history_id,
							$log_useragent,
							$is_private_browsing_mode,
							$first_access_datetime,
							$upl{4},
							$upl{5},
							$upl{6},
							"\n"
					));
#					$res++;

					# 最終投稿者名と時間を覚えておく
					$last_nam = $nam;
					$last_dat = $da;
					# タイトルも
					$last_sub = $sub;
				}
			}
			close(DAT);

			# 新規スレッド作成
			# indexファイル
			local($new, $top, @new, @top, @faq);
			open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
			eval "flock(DAT, 2);";
			$top = <DAT>;
			local($no,$host2,$time2) = split(/<>/, $top);

			$new = $no + 1;

			# index展開
			while(<DAT>) {
				local($sub,$key) = (split(/<>/))[1,6];

#				$i++;
#				if ($sub eq $in{'sub'}) { $flg++; last; }
				if ($key == 2) { push(@top,$_); next; }
				if ($key == 3) { push(@faq,$_); next; }

# 				この作業時は過去ログに落とさない
#				if ($i >= $i_max) { push(@tmp,$_); }
				else { push(@new,$_); }
			}

			# ファイルアップ
			# レスには画像がついていないはずだから無視

			# 現行index更新
			unshift(@new,"$new<>$sub2<>$res<>$i_nam2<>$i_da<>$last_nam<>1<><>$last_sub<>$i_tim<>$i_ho<>\n");
			unshift(@new,@faq) if (@faq > 0);
			unshift(@new,@top) if (@top > 0);
			unshift(@new,"$new<>$host2<>$time2<>\n");
			seek(DAT, 0, 0);
			print DAT @new;
			truncate(DAT, tell(DAT));
			close(DAT);

			# スレッド更新
			my $new_logfolder_path = get_logfolder_path($new);
			my $new_logfile_path = "$new_logfolder_path/$new.cgi";
			if (!-e $new_logfolder_path) {
				mkdir($new_logfolder_path);
				chmod (0777, $new_logfolder_path);
			}
			open(OUT, ">", $new_logfile_path) || &error("Write Error: $new.cgi");
			print OUT "$new<>$sub2<>$res<>1<>\n";
			print OUT @newt;
			close(OUT);

			# パーミッション変更
			chmod(0666, $new_logfile_path);

			# スレッド更新日時管理データベースに、分割後の新しいスレッド情報を追加
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$updatelog_db->create_threadinfo($new, $i_tim, 1);
			$updatelog_db->close(0);
		}

		# スレッド内個別閲覧
		&header;
		print "<div align=\"right\">\n";
		print "<form action=\"$admincgi\" method=\"post\">\n";
		print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
		print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
		print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
		print "<input type=\"submit\" value=\"&lt;&lt; 戻る\"></form></div>\n";
		print "<form action=\"$admincgi\" method=\"post\">\n";
		print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
		print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
		print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
		print "<input type=\"hidden\" name=\"no\" value=\"$in{'no'}\">\n";
		print "<input type=\"hidden\" name=\"action\" value=\"view\">\n";

		my $logfile_path = get_logfolder_path($in{'no'}) . "/$in{'no'}.cgi";
		open(IN, $logfile_path);
		$top = <IN>;
		($num,$sub,$res,$key) = split(/<>/, $top);
		$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

		print "スレッド名 ： <b>$sub</b> [ $subject ]<hr>\n";
		print "キー状態 : $key<br>\n";
		print "<li>修正又は削除を選択して記事をチェックします。<br>\n";
		print "<li>親記事の削除はできません。<br><br>\n";
		print "処理 ： <select name=\"job\">\n";
		print "<option value=\"edit\" selected>修正\n";
		print "<option value=\"del\">削除\n";
		print "<option value=\"split\">分割</select>\n";
		print "<input type=\"submit\" value=\"送信する\">\n";
		print "<dl>\n";

		while (<IN>) {
			chomp($_);
			local($no,$sub,$nam,$em,$com,$da,$ho,$pw,$url,$mvw,$myid,$user_id,$is_sage,$cookie_a,$history_id) = (split(/<>/))[0..10,16..19];
			$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

			if ($em) { $nam="<a href=\"mailto:$em\">$nam</a>"; }

			print "<dt><input type=\"checkbox\" name=\"no2\" value=\"$no\"> ";
			print "[<b>$no</b>] $sub <b>$nam</b>";
			if ($is_sage eq '1') { print ' [sage]'; }
			print " - $da ";
			print "【<font color=\"$al\">$ho</font>】\n";

			if ($authkey) { print "ID:$myid\n"; }

			if ($user_id) { print " 登録ID:$user_id\n"; }

			if ($history_id ne '') { print " 書込ID:$history_id\n"; }

			if ($cookie_a) { print " CookieA:$cookie_a\n"; }

			print "<dd>$com\n";
		}
		close(IN);

		print "</dl></form>\n</body></html>\n";
		exit;
	}

# スレッド操作メニュー

	&header;
	print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<h3 style="font-size:16px">管理モード [ $subject ]</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="$mylog" value="1">
スレッド処理 <select name="action">
<option value="view">個別メンテ
<option value="del">スレ削除
EOM

#	if ($in{'past'} == 0) {
# 過去ログではいじれないように（というかいじれても変）
	if ($in{'logfile'}) {
		print "<option value=\"lock\">ロック開閉\n";
		print "<option value=\"lock2\">管理者\n";
		print "<option value=\"faq\">ＦＡＱ\n";
# }
#
# 	if ($in{'logfile'}) {
		print "<option value=\"archive\">過去ログ化\n";
	}

	if ($in{'bakfile'}) {
		print "<option value=\"extract\">現行ログ化\n";
	}

	print <<EOM;
</select>
<input type="submit" value="送信する">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="400">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="4" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" nowrap>選択</td>
  <td bgcolor="$col3" width="100%">&nbsp; スレッド</td>
  <td bgcolor="$col3" align="center" nowrap>レス数</td>
</tr>
EOM

	# スレッド一覧
	open(IN,"$log") || &error("Open Error: $log");
	$top = <IN> if (!$in{'bakfile'});
	while (<IN>) {
		local($no,$sub,$res,$nam,$da,$na2,$key,$upl,$ressub,$restime) = split(/<>/);
		$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除

		print "<tr bgcolor=\"$col2\"><th bgcolor=\"$col2\">";
		print "<input type=checkbox name=\"no\" value=\"$no\"></th>";
		print "<td bgcolor=\"$col2\">";

		if ($key eq '0') {
			print "[<font color=\"$al\">ロック中</font>] ";
		} elsif ($key == 2) {
			print "[<font color=\"$al\">管理コメント</font>] ";
		} elsif ($key == 3) {
			print "[<font color=\"$al\">FAQ</font>] ";
		} elsif ($key == 4) {
			print "[<font color=\"$al\">管理者ロック中</font>] ";
		} elsif ($key == -1) {
			print "[<font color=\"$al\">過去ログ</font>] ";
		}

		print "<b><a href=\"$readcgi?no=$no\">[$no] $sub</a></b></td>";
		print "<td bgcolor=\"$col2\" align=\"center\">$res</td></tr>\n";
	}
	close(IN);

	print <<EOM;
</table>
</Td></Tr></Table>
</form>
</body>
</html>
EOM

	exit;
}

#-------------------------------------------------
#  ファイルサイズ
#-------------------------------------------------
sub filesize {
	local($top,$tmp,$num,$all,$all2,$size1,$size2,$size3,$size4,$file,$file1,$file2);

	# 現行ログ
	$size1 = 0;
	$file1 = 0;
	open(IN,"$nowfile") || &error("Open Error: $nowfile");
	$top = <IN>;
	while (<IN>) {
		($num) = split(/<>/);
		$tmp = -s get_logfolder_path($num) . "/$num.cgi";
		$size1 += $tmp;
		$file1++;

		$now{$num} = 1;
	}
	close(IN);

	# 過去ログ
	$size2 = 0;
	$file2 = 0;
	open(IN,"$pastfile") || &error("Open Error: $pastfile");
	while (<IN>) {
		($num) = split(/<>/);
		$tmp = -s get_logfolder_path($num) . "/$num.cgi";
		$size2 += $tmp;
		$file2++;

		$pst{$num} = 1;
	}
	close(IN);

	# 画像容量算出サブルーチン定義
	local $calc_img = sub {
		my ($ref_counter, $file_regex, $dir, $is_recursive) = @_;

		# ディレクトリ内一覧を取得
		opendir(my $dir_fh, $dir) || return;
		my @dir_list = readdir($dir_fh);
		closedir($dir_fh);

		# 指定正規表現に合致するファイルのサイズを合計
		# サブディレクトリは専用のリストに追加
		my @subdir_list;
		my $exclude_subdir_regex = qr/^\.{1,2}$/;
		foreach my $pathname (@dir_list) {
			if (-f "$dir/$pathname" && $pathname =~ /$file_regex/) {
				${$ref_counter} += -s "$dir/$pathname";
			} elsif (-d "$dir/$pathname" && $pathname !~ /$exclude_subdir_regex/) {
				push(@subdir_list, "$dir/$pathname");
			}
		}

		# 再帰検索が有効の場合には、サブディレクトリリストを使い
		# 本サブルーチンを再帰呼び出し
		if ($is_recursive) {
			foreach my $subdir (@subdir_list) {
				$calc_img->($ref_counter, $file_regex, $subdir, 1);
			}
		}
	};

	# 画像
	my $img = 0;
	$calc_img->(\$img, qr/^\d+-\d\.(jpg|gif|png)$/, $upldir, 1);

	# サムネイル画像
	my $thumb = 0;
	$calc_img->(\$thumb, qr/^\d+-\d_s\.jpg$/, $thumbdir, 1);

	$size1 = int ($size1 / 1024 + 0.5);
	$size2 = int ($size2 / 1024 + 0.5);
	$img   = int ($img / 1024 + 0.5);
	$thumb = int ($thumb / 1024 + 0.5);
	$all = $size1 + $size2;
	$file = $file1 + $file2;

	&header;
	print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<h3 style="font-size:16px">ログ容量算出</h3>
<ul>
<li>以下は記録ファイルの容量（サイズ）で、小数点以下は四捨五入します。
<li>分類欄のフォームをクリックすると各管理画面に移動します。
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="280">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" rowspan="2" align="center">分類</td>
  <td bgcolor="$col3" rowspan="2" width="70" align="center">ファイル数</td>
  <td bgcolor="$col3" colspan="3" align="center">サイズ</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" width="50">ログ</td>
  <td bgcolor="$col3" align="center" width="50">画像</td>
  <td bgcolor="$col3" align="center" width="50">サムネイル</td>
</tr>
<tr>
  <th bgcolor="$col2">
   <form action="$admincgi" method="post">
   <input type="submit" name="logfile" value="現行ログ"></th>
  <td align="right" bgcolor="$col2">$file1</td>
  <td align="right" bgcolor="$col2">$size1 KB</td>
  <td align="right" bgcolor="$col2" rowspan="2">$img KB</td>
  <td align="right" bgcolor="$col2" rowspan="2">$thumb KB</td>
</tr>
<tr bgcolor="$col2">
  <th bgcolor="$col2">
   <input type="submit" name="bakfile" value="過去ログ"></th>
  </th>
  <td align="right" bgcolor="$col2">$file2</td>
  <td align="right" bgcolor="$col2">$size2 KB</td>
</tr>
<tr bgcolor="$col2">
  <th bgcolor="$col2">合計</th>
  <td align="right" bgcolor="$col2">$file</td>
  <td align="right" bgcolor="$col2">$all KB</td>
  <td align="right" bgcolor="$col2">$img KB</td>
  <td align="right" bgcolor="$col2">$thumb KB</td>
</tr>
</table>
</Td></Tr></Table>
</form>
</ul>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  会員管理
#-------------------------------------------------
sub member_mente {
	# 新規フォーム
	if ($in{'job'} eq "new") {

		&member_form();

	# 新規発行
	} elsif ($in{'job'} eq "new2") {

		local($err);
		if (!$in{'name'}) { $err .= "名前が未入力です<br>\n"; }
		if ($in{'myid'} =~ /\W/) { $err .= "IDは英数字のみです<br>\n"; }
		if (length($in{'myid'}) < 4 || length($in{'myid'}) > 8) {
			$err .= "IDは英数字で4～8文字です<br>\n";
		}
		if ($in{'mypw'} =~ /\W/) { $err .= "パスワードは英数字のみです<br>\n"; }
		if (length($in{'mypw'}) < 4 || length($in{'mypw'}) > 8) {
			$err .= "パスワードは英数字で4～8文字です<br>\n";
		}
		if (!$in{'rank'}) { $err .= "権限が未選択です<br>\n"; }
		if ($err) { &error($err); }

		local($flg,$crypt,$id,$pw,$rank,$nam,@data);

		# IDチェック
		$flg = 0;
		open(DAT,"+< $memfile") || &error("Open Error: $memfile");
		while(<DAT>) {
			local($id,$pw,$rank,$nam) = split(/<>/);

			if ($in{'myid'} eq $id) { $flg = 1; last; }
			push(@data,$_);
		}

		if ($flg) { &error("このIDは既に登録済です"); }

		# パス暗号化
		$crypt = &encrypt($in{'mypw'});

		# 更新
		seek(DAT, 0, 0);
		print DAT "$in{'myid'}<>$crypt<>$in{'rank'}<>$in{'name'}<>\n";
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# 修正フォーム
	} elsif ($in{'job'} eq "edit" && $in{'myid'}) {

		if ($in{'myid'} =~ /\0/) { &error("修正選択は１つのみです"); }

		local($flg,$id,$pw,$rank,$nam);

		$flg = 0;
		open(IN,"$memfile") || &error("Open Error: $memfile");
		while (<IN>) {
			($id,$pw,$rank,$nam) = split(/<>/);

			if ($in{'myid'} eq $id) { $flg = 1; last; }
		}
		close(IN);

		&member_form($id,$pw,$rank,$nam);

	# 修正実行
	} elsif ($in{'job'} eq "edit2") {

		local($err,$crypt);
		if (!$in{'name'}) { $err .= "名前が未入力です<br>\n"; }
		if ($in{'myid'} =~ /\W/) { $err .= "IDは英数字のみです<br>\n"; }
		if (length($in{'myid'}) < 4 || length($in{'myid'}) > 8) {
			$err .= "IDは英数字で4～8文字です<br>\n";
		}
		if ($in{'chg'}) {
			if ($in{'mypw'} =~ /\W/) { $err .= "パスワードは英数字のみです<br>\n"; }
			if (length($in{'mypw'}) < 4 || length($in{'mypw'}) > 8) {
				$err .= "パスワードは英数字で4～8文字です<br>\n";
			}

			# パス暗号化
			$crypt = &encrypt($in{'mypw'});

		} elsif (!$in{'chg'} && $in{'mypw'} ne "") {
			$err .= "パスワードの強制変更はチェックボックスに選択してください<br>\n";
		}
		if (!$in{'rank'}) { $err .= "権限が未選択です<br>\n"; }
		if ($err) { &error($err); }

		local($flg,$id,$pw,$rank,$nam,@data);

		open(DAT,"+< $memfile") || &error("Open Error: $memfile");
		while(<DAT>) {
			local($id,$pw,$rank,$nam) = split(/<>/);

			if ($in{'myid'} eq $id) {
				if ($crypt) { $pw = $crypt; }
				$_ = "$id<>$pw<>$in{'rank'}<>$in{'name'}<>\n";
			}
			push(@data,$_);
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# 削除
	} elsif ($in{'job'} eq "dele" && $in{'myid'}) {

		local($flg,@data,@del);

		# 削除情報
		@del = split(/\0/, $in{'myid'});

		open(DAT,"+< $memfile") || &error("Open Error: $memfile");
		while(<DAT>) {
			local($id,$pw,$rank,$nam) = split(/<>/);

			$flg = 0;
			foreach $del (@del) {
				if ($del eq $id) { $flg = 1; last; }
			}
			if (!$flg) { push(@data,$_); }
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	&header;
	print <<"EOM";
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<h3 style="font-size:16px">会員管理</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="hidden" name="past" value="3">
処理 :
<select name="job">
<option value="new">新規
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="280">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="3" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" nowrap width="30">選択</td>
  <td bgcolor="$col3" align="center" nowrap>ID</td>
  <td bgcolor="$col3" align="center" nowrap>名前</td>
  <td bgcolor="$col3" align="center" nowrap>ランク</td>
</tr>
EOM

	open(IN,"$memfile") || &error("Open Error: $memfile");
	while (<IN>) {
		($id,$pw,$rank,$nam) = split(/<>/);

		print "<tr bgcolor=\"$col2\"><th bgcolor=\"$col2\">";
		print "<input type=\"checkbox\" name=\"myid\" value=\"$id\"></th>";
		print "<td bgcolor=\"$col2\" nowrap>$id</td>";
		print "<td bgcolor=\"$col2\">$nam</td>";
		print "<td bgcolor=\"$col2\" align=\"center\">$rank</td>";
	}
	close(IN);

	print <<EOM;
</table>
</Td></Tr></Table>
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  会員フォーム
#-------------------------------------------------
sub member_form {
	local($id,$pw,$rank,$nam) = @_;
	local($job) = $in{'job'} . '2';

	&header();
	print <<EOM;
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="submit" value="&lt; 前画面">
</form>
<h3 style="font-size:16px">登録フォーム</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="hidden" name="job" value="$job">
<Table border="0" cellspacing="0" cellpadding="0" width="350">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>名前</td>
  <td bgcolor="$col2"><input type="text" name="name" size="25" value="$nam"></td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>ログインID</td>
  <td bgcolor="$col2">
EOM

	if ($in{'myid'}) {
		print $in{'myid'};
	} else {
		print "<input type=\"text\" name=\"myid\" size=\"10\" value=\"$id\">\n";
		print "（英数字で4～8文字）\n";
	}

	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>パスワード</td>
  <td bgcolor="$col2">
	<input type="password" name="mypw" size="10"> （英数字で4～8文字）
EOM

	if ($in{'myid'}) {
		print "<br><input type=\"checkbox\" name=\"chg\" value=\"1\">\n";
		print "パスワードを強制変更する場合にチェック\n";
		print "<input type=\"hidden\" name=\"myid\" value=\"$in{'myid'}\">\n";
	}

	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>権限</td>
  <td bgcolor="$col2">
EOM

	local(%rank) = (1,"閲覧のみ", 2,"閲覧&amp;書込OK");
	foreach (1,2) {
		if ($rank == $_) {
			print "<input type=radio name=rank value=\"$_\" checked>レベル$_ ($rank{$_})<br>\n";
		} else {
			print "<input type=radio name=rank value=\"$_\">レベル$_ ($rank{$_})<br>\n";
		}
	}

	print <<EOM;
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
<input type="submit" value="送信する">
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  メニュー画面
#-------------------------------------------------
sub menu_disp {
	# セッションディレクトリ掃除
	if ($authkey && $in{'login'}) {
		&ses_clean;
	}

	&header;
	print <<EOM;
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<div align="center">
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="job" value="menu">
処理内容を選択してください。
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="320">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center">
	選択
  </td>
  <td bgcolor="$col3" width="100%">
	&nbsp; 処理内容
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="logfile" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; 現行ログ・メンテナンス
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="bakfile" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; 過去ログ・メンテナンス
  </td>
</tr>
EOM

	if ($authkey) {
		print "<tr bgcolor=\"$col2\"><td bgcolor=\"$col2\" align=\"center\">\n";
		print "<input type=\"submit\" name=\"member\" value=\"選択\"></td>";
		print "<td bgcolor=\"$col2\" width=\"100%\">&nbsp; 会員認証の管理</td></tr>\n";
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="filesize" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; ファイル容量の閲覧
  </td>
</tr>
EOM

	if ($createonlyadmin) {
	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	&nbsp;
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; 	<a href="$readcgi?mode=form">新規スレッド作成（スレッド作成制限中）</a>
  </td>
</tr>
EOM
}

	if($conf_override) {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="config_override_settings" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; 動作設定
  </td>
</tr>
EOM
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="rebuild_thread_updatelog_db" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; スレッド更新日時管理データベース 再構\築
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
    <input type="submit" name="move_threadlog" value="選択">
  </td>
  <td bgcolor="$col2" width="100%">
    &nbsp; スレッドログファイル 保存フォルダ再配置処理
  </td>
</tr>
</table>
</Td></Tr></Table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  入室画面
#-------------------------------------------------
sub enter {
	&header;
	print <<EOM;
<blockquote>
<table border="0" cellspacing="0" cellpadding="26" width="400">

EOM
	if($in{'action'} eq 'log' && $in{'file'}) {
		my $logfile_path = get_logfolder_path($in{'file'}) . "/$in{'file'}.cgi";
		my @title;
		open(my $log_fh, $logfile_path) || &error("Open Error: $in{'file'}.cgi");
		flock($log_fh, 1) || &error("Lock Error: $in{'file'}.cgi");
		$i = 1;
		while(<$log_fh>) {
			$_ =~ s/(?:\r\n|\n\r|\r|\n)$//;
			if($i eq 1) {
				push(@title, split(/<>/));
			}
			break;
		}
		close($log_fh);

		print <<EOM;
	<tr><td align="left">
	<div style="font-size:16px;">【ログの閲覧】</div>
	<div style="margin:5px 0 5px 0;">件名:@title[1]</div>
	<form action="$admincgi" method="post">
	    <input type="hidden" name="action" value="log">
	    <input type="hidden" name="file" value="$in{'file'}">
		<input type="hidden" name="login" value="1">
		<label id="id_pass">パスワード<label>
		<input id="id_pass" type="password" name="pass" size="16">
		<input type="submit" value=" 送信する ">
	</form>
	<form action="$admincgi" method="post">
	    <input type="hidden" name="action" value="log">
	    <input type="hidden" name="file" value="$in{'file'}">
		<input type="hidden" name="cookie_id" value="on">
		<input type="submit" style="margin-top:5px;" value=" 書込IDで認証 ">
	</form>
	</td></tr>
EOM
	}
	else{
		print <<EOM;
	<tr><td align="center">
	<fieldset>
	<legend>
	▼管理パスワード入力
	</legend>
	<form action="$admincgi" method="post">
		<input type="hidden" name="login" value="1">
		<input type="password" name="pass" size="16">
		<input type="submit" value=" 認証 "></form>
	</fieldset>
	</td></tr>
EOM
	}
	print <<EOM;
</table>
</blockquote>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  セションディレクトリ掃除
#-------------------------------------------------
sub ses_clean {
	local($mtime,@dir);

	opendir(DIR,"$sesdir");
	@dir = readdir(DIR);
	closedir(DIR);

	foreach (@dir) {
		next unless (/^\w+\.cgi$/);

		$mtime = (stat("$sesdir/$_"))[9];
		if (time - $mtime > $authtime*60*2) {
			unlink("$sesdir/$_");
		}
	}
}

#-------------------------------------------------
#  動作設定
#-------------------------------------------------
sub config_override_settings {
	if(!$conf_override) {
		&menu_disp;
	}

	# 設定値ファイル書き込み
	my $update_flg;
	if($in{'action'}) {
		$update_flg = 1;

		# 設定値チェック
		my $err;
		if(!$in{'img_default'}
			&& (
					($in{'img_width'} !~ /^\d*$/ || int($in{'img_width'})< 0)
					|| ($in{'img_height'} !~ /^\d*$/ || int($in{'img_height'})< 0)
				)
			) {
			if($thumbnail) {
				$err .= "サムネイル";
			} else {
				$err .= "アップロード";
			}
			$err .= "画像 表\示サイズの指定が正しくありません。<br>\n";
		}
		if($in{'thumb_enabled'} && !$in{'thumb_default'}
			&& (
					($in{'thumb_width'} !~ /^\d*$/ || int($in{'thumb_width'})< 0)
					|| ($in{'thumb_height'} !~ /^\d*$/ || int($in{'thumb_height'})< 0)
				)
			) {
			$err .= "サムネイル画像 生成サイズの指定が正しくありません。<br>\n";
		}
		if(!$in{'uploadext_default'}) {
			my @exts = grep { $_ =~ /^uploadext_\d*_[a-z]*$/ } sort keys %in;
			for(my $i=0; $i<$#exts+1; $i++) {
				if($in{$exts[$i]} !~ /^[01]$/) {
					$err .= "アップロード可能ファイル拡張子のPOST値が異常です<br>\n";
				}
			}
		}
		if($err) { &error($err); }

		# Shebangを$admincgiより取得
		open(ADMIN, "$admincgi") || &error("Open Error: $admincgi");
		my $shebang = <ADMIN>;
		close(ADMIN);

		# $conf_override_pathファイルを新規作成するかどうかを取得
		my $existOverrideConf = -f $conf_override_path;

		# 設定値を$conf_override_pathファイルに書き込み
		open(OVERRIDECONF, "> $conf_override_path") || &error("Open Error: $conf_override_path");
		eval "flock(OVERRIDECONF, 2)";
		print OVERRIDECONF $shebang . "\n";
		print OVERRIDECONF <<"EOM";
#-------------------------------------------------------#
# WebPatio 動作設定管理ファイル                         #
#                                                       #
# このファイルは管理画面-動作設定セクションの設定により #
# 自動生成されているため、内容を変更しないで下さい。    #
#-------------------------------------------------------#

EOM
		if($in{'img_default'}) {
			undef $override_img_max_w;
			undef $override_img_max_h;
			$img_max_w = $default_img_max_w;
			$img_max_h = $default_img_max_h;
		} else {
			print OVERRIDECONF "# アップロード画像表\示サイズ(サムネイル画像機能\有効時はサムネイル画像表\示サイズ)\n";
			print OVERRIDECONF "\$override_img_max_w = " . int($in{'img_width'}) . ";\n";
			print OVERRIDECONF "\$override_img_max_h = " . int($in{'img_height'}) . ";\n\n";
			$img_max_w = int($in{'img_width'});
			$img_max_h = int($in{'img_height'});
			$override_img_max_w = $img_max_w;
			$override_img_max_h = $img_max_h;
		}

		if($in{'thumb_enabled'}) {
			if($in{'thumb_default'}) {
				undef $override_thumb_max_w;
				undef $override_thumb_max_h;
				$thumb_max_w = $default_thumb_max_w;
				$thumb_max_h = $default_thumb_max_h;
			} else {
				print OVERRIDECONF "# サムネイル画像生成サイズ\n";
				print OVERRIDECONF "\$override_thumb_max_w = " . int($in{'thumb_width'}) . ";\n";
				print OVERRIDECONF "\$override_thumb_max_h = " . int($in{'thumb_height'}) . ";\n\n";
				$thumb_max_w = int($in{'thumb_width'});
				$thumb_max_h = int($in{'thumb_height'});
				$override_thumb_max_w = $thumb_max_w;
				$override_thumb_max_h = $thumb_max_h;
			}
		}

		if($in{'uploadext_default'}) {
			undef %override_imgex;
			%imgex = %default_imgex;
		} else {
			print OVERRIDECONF "# アップロード画像ファイル拡張子\n";
			print OVERRIDECONF "\%override_imgex = (";
			my @exts = grep { $_ =~ /^uploadext_\d*_[a-z]*$/ } sort keys %in;
			for(my $i=0; $i<$#exts+1; $i++) {
				my $ext = $exts[$i];
				$ext =~ s/^uploadext_\d*_/./;
				print OVERRIDECONF "\"$ext\",$in{$exts[$i]}";
				$imgex{$ext} = int($in{$exts[$i]});
				if($i<$#exts) {
					print OVERRIDECONF ",";
				}
			}
			print OVERRIDECONF ");\n\n";
			%override_imgex = %imgex;
		}
		my $enableExtCount = 0;
		$enableExtCount += $_ for values(%imgex);
		if(!$enableExtCount) {
			# アップロード可能ファイル拡張子が一つもないときは、アップロード機能を停止
			$image_upl = 0;
		}

		print OVERRIDECONF "1;\n";
		close(OVERRIDECONF);

		# 設定ファイルを新規に作成した場合は、パーミッションを設定
		if(!$existOverrideConf) {
			chmod 0777, $conf_override_path;
		}
	}
	# アップロード可能ファイル拡張子をハッシュからソートして取得
	my @sort_ext_keys = sort keys %imgex;

	&header;
	print <<"EOM";
<script type="text/javascript">
  function refreshDisplaySizeConfigState() {
    if(document.forms[2].elements["img_default"].checked) {
      document.forms[2].elements["img_width"].value = ${default_img_max_w};
      document.forms[2].elements["img_height"].value = ${default_img_max_h};
    }
    document.forms[2].elements["img_width"].disabled = document.forms[2].elements["img_default"].checked;
    document.forms[2].elements["img_height"].disabled = document.forms[2].elements["img_default"].checked;
  }

EOM
	if($thumbnail) {
		print <<"EOM";
  function refreshThumbnailSizeConfigState() {
    if(document.forms[2].elements["thumb_default"].checked) {
      document.forms[2].elements["thumb_width"].value = ${default_thumb_max_w};
      document.forms[2].elements["thumb_height"].value = ${default_thumb_max_h};
    }
    document.forms[2].elements["thumb_width"].disabled = document.forms[2].elements["thumb_default"].checked;
    document.forms[2].elements["thumb_height"].disabled = document.forms[2].elements["thumb_default"].checked;
  }

EOM
	}

	print "  function refreshExtensionConfigState() {\n";
	print "    var default_state = [";
	for(my $i=0; $i<$#sort_ext_keys+1; $i++) {
		my $ext = $sort_ext_keys[$i];
		$ext =~ s/^\.//;
		print "[\"$ext\",$default_imgex{$sort_ext_keys[$i]}]";
		if($i != $#sort_ext_keys) {
			print ",";
		}
	}
	print "];\n";
	print <<"EOM";
    if(document.forms[2].elements[\"uploadext_default\"].checked) {
EOM
	print "      for(var i=0; i<" . ($#sort_ext_keys+1) . "; i++) {\n";
	print <<"EOM";
        document.getElementById("uploadext_" + i).checked = default_state[i][1] == 1 ? true : false;
        document.getElementById("uploadext_" + i).disabled = true;
        document.forms[2].elements["uploadext_" + i + "_" + default_state[i][0]].value = default_state[i][1];
      }
    } else {
EOM
	print "      for(var i=0; i<" . ($#sort_ext_keys+1) . "; i++) {\n";
	print <<"EOM";
        document.getElementById("uploadext_" + i).disabled = false;
        document.forms[2].elements["uploadext_" + i + "_" + default_state[i][0]].value = document.getElementById("uploadext_" + i).checked ? 1 : 0;
      }
    }
  }
</script>
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="config_override_settings" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">動作設定　<input type="submit" value="送信する"></h3>
EOM
	if($update_flg) { print "<font color=\"red\"><b>設定を更新しました</b></font>\n"; }
	print <<"EOM";
<p>
<Table border="0" cellspacing="0" cellpadding="0">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="4">
<tr bgcolor="$col3">
  <th align="center">項目名</th>
  <th width="100%">設定内容</th>
</tr>
EOM
	# アップロード画像表示サイズ設定(サムネイル画像機能有効時はサムネイル画像表示サイズ)
	print "<tr bgcolor=\"$col2\">\n";
	print "  <th align=\"center\" nowrap>";
	if($thumbnail) {
		print "サムネイル";
	} else {
		print "アップロード";
	}
	print "画像 表\示サイズ</th>\n";
	print <<"EOM";
  <td>
    <div align="center">
EOM
	print "      幅 <input type=\"text\" name=\"img_width\" size=\"5\" value=\"$img_max_w\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " disabled=\"disabled\"";
	}
	print "> px&nbsp;\n";
	print "      高さ <input type=\"text\" name=\"img_height\" size=\"5\" value=\"$img_max_h\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " disabled=\"disabled\"";
	}
	print "> px\n";
	print "    </div>\n";
	print "    <input type=\"checkbox\" name=\"img_default\" value=\"1\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " checked";
	}
	print " onchange=\"refreshDisplaySizeConfigState();\"> init.cgi設定値を使用 (幅 ${default_img_max_w}px 高さ${default_img_max_h}px)\n";
	print <<"EOM";
  </td>
</tr>
EOM

	# サムネイル画像生成サイズ設定
	if($thumbnail) {
		print <<"EOM";
<tr bgcolor="$col2">
  <th align="center" nowrap>サムネイル画像 生成サイズ</th>
  <td>
    <div align="center">
EOM
		print "      幅 <input type=\"text\" name=\"thumb_width\" size=\"5\" value=\"$thumb_max_w\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " disabled=\"disabled\"";
		}
		print "> px&nbsp;\n";
		print "      高さ <input type=\"text\" name=\"thumb_height\" size=\"5\" value=\"$thumb_max_h\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " disabled=\"disabled\"";
		}
		print "> px\n";
		print "    </div>\n";
		print "    <input type=\"checkbox\" name=\"thumb_default\" value=\"1\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " checked";
		}
		print " onchange=\"refreshThumbnailSizeConfigState();\"> init.cgi設定値を使用 (幅 ${default_thumb_max_w}px 高さ${default_thumb_max_h}px)\n";
		print <<"EOM";
    <input type="hidden" name="thumb_enabled" value="1">
  </td>
</tr>
EOM
	}

	# アップロード可能ファイル拡張子選択
	print <<"EOM";
<tr bgcolor="$col2">
  <th align="center" nowrap>アップロー\ド可能\ファ\イル拡張子</th>
  <td>
EOM
	for(my $i=0; $i<$#sort_ext_keys+1; $i+=3) {
		for(my $j=$i; $j<$i+3 && $j<$#sort_ext_keys+1; $j++) {
			my $ext = $sort_ext_keys[$j];
			$ext =~ s/^\.//;
			my $uc_ext = uc $ext;
			print "    <input type=\"checkbox\" id=\"uploadext_$j\" onclick=\"refreshExtensionConfigState();\"";
			if($imgex{$sort_ext_keys[$j]}) {
				print " checked";
			}
			if(!%override_imgex) {
				print " disabled=\"disabled\"";
			}
			print "> $uc_extファ\イル";
			print "<input type=\"hidden\" name=\"uploadext_${j}_$ext\" value=\"$imgex{$sort_ext_keys[$j]}\">\n";
		}
		print "    <br>\n";
	}
	print "    <input type=\"checkbox\" name=\"uploadext_default\" value=\"1\"";
	if(!%override_imgex) {
		print " checked";
	}
	print " onchange=\"refreshExtensionConfigState();\"> init.cgi設定値を使用\n";
	print <<"EOM";
  </td>
</tr>
</table>
</Td></Tr></Table>
EOM

	# サムネイル画像機能無効時の生成サイズ設定値を非表示のまま送信するためのinputタグ
	if(!$thumbnail && defined $override_thumb_max_w && defined $override_thumb_max_h) {
		print <<"EOM";
<input type="hidden" name="thumb_width" value="$thumb_max_w">
<input type="hidden" name="thumb_height" value="$thumb_max_h">
<input type="hidden" name="thumb_enabled" value="1">
EOM
	}

	print <<"EOM";
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  スレッド更新日時管理データベース 再構築
#-------------------------------------------------
sub rebuild_thread_updatelog_db {
	my $rebuild_flg = 0;
	if($in{'action'}) {
		$rebuild_flg = 1;

		# スレッド更新日時管理データベース再構築処理
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->rebuild_database($logdir);
		$updatelog_db->close(0);
	}
	&header;
	print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<form action="$admincgi" method="post" id="adminCGI">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="rebuild_thread_updatelog_db" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">スレッド更新日時管理データベース 再構\築</h3>
EOM
	if($rebuild_flg) { print "<font color=\"red\"><b>スレッド更新日時管理データベースを再構\築しました</b></font>\n"; }
	print <<"EOM";
<p>
全てのログファイルを読み込み、スレッド更新日時管理データベースを再構\築します。<br>
ログファイルの件数によっては処理に時間がかかることがあります。
<p>
また、処理中はデータベースへのアクセスができないため、<br>
データベースへのアクセスが伴う、スレッドやレスの作成・変更・削除、検索機能\がロックされ、<br>
利用できなくなりますのでご注意下さい。
<p>
<input type="submit" id="doRebuild" value="再構\築処理を開始する" onClick='if(confirm("本当に開始してもよろしいですか？")) { \$("#doRebuild").prop("disabled", true).val("再構\築処理中です..."); \$("#adminCGI").submit(); } return false;'>
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  スレッドログファイル 保存フォルダ再配置処理
#-------------------------------------------------
sub move_threadlog {
	if ($in{'action'}) {
		### 保存フォルダ再配置処理 実行 ###

		# ロックファイル作成・ロック処理
		my ($lock_exist, $lock_fh) = -e $thread_log_moving_lock_path;
		open($lock_fh, '>>', $thread_log_moving_lock_path) || error("ロックファイル($thread_log_moving_lock_path)をオープンできませんでした");
		flock($lock_fh, 6) || error("別プロセスで再配置処理が実行中である可能\性があるため、処理を開始できませんでした");

		# ヘッダー出力
		header("スレッドログファイル 保存フォルダ再配置処理", undef, 1); # バッファリングを無効にして進捗表示を行う
		print <<EOM;
<div>
<h1>スレッドログファイル 保存フォルダ再配置処理</h1>
EOM
		if ($lock_exist) {
			print <<EOM;
<p style="color: #cc0000">
前回の再配置処理が正常に終了していない可能\性があります。<br>
再度、適切なフォルダへの再配置処理を行います。
</p>
EOM
		}
		print <<EOM;
</div>
<div>
<p>
スレッドログファイルの保存フォルダ再配置処理を開始します。
</p>
EOM

		# スレッドログファイル リスト取得
		print "<p>\nスレッドログファイル情報を取得しています... ";
		my @original_path_list = do {
			# スレッドログファイル リスト取得
			my @log_paths = File::Find::Rule->file->name(qr/^\d*\.cgi$/)->in($logdir);
			# スレッド番号 => ファイルパス リストインデックス のハッシュを作り、
			# キー(スレッド番号)で昇順ソート、対応するインデックスから
			# 昇順ソートしたスレッドログファイル リストを返す
			my %log_number_array_index_hash = map { basename($log_paths[$_], '.cgi') => $_ } 0 .. $#log_paths;
			map { $log_paths[$log_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%log_number_array_index_hash);
		};
		print "<span style=\"color: #66cc66\">OK</span>\n</p>\n";

		# 再配置処理
		my $error = 0;
		my @moved_path_list; # 再配置済みファイルパス リスト
		while (my $original_path = File::Spec->canonpath(shift(@original_path_list))) { # ファイルを1つずつ再配置処理
			# 再配置先パス情報を取得
			my $thread_number = basename($original_path, '.cgi');
			my $logfolder_path = File::Spec->canonpath(get_logfolder_path($thread_number));
			my $replace_path = File::Spec->canonpath("$logfolder_path/$thread_number.cgi");

			# 再配置先パスが現存パスと同一の場合にはスキップ
			if ($replace_path eq $original_path) {
				print "$original_path == $replace_path ... <span style=\"color: #006600\">Skip</span><br>\n";
				next;
			}

			# 再配置先フォルダが存在しない場合は作成する (存在する場合は書き込み権限を確認)
			if (!-e $logfolder_path) {
				print "【フォルダ作成】 $logfolder_path を作成します... ";
				if(mkdir($logfolder_path) && chmod(0777, $logfolder_path)) {
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">失敗しました</span><br>\n";
					$error = 1;
				}
			} else {
				if (!-w $logfolder_path) {
					print "<span style=\"color: #cc0000; font-weight:bold\">$logfolder_path のパーミッションが正しく設定されているか確認して下さい</span><br>\n";
					$error = 1;
				}
			}

			# 再配置
			if (!$error) {
				print "$original_path -> $replace_path ... ";
				if (move($original_path, $replace_path)) {
					push(@moved_path_list, $original_path);
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">失敗しました</span><br>\n";
					$error = 1;
				}
			}

			# エラー発生時はロールバック
			if ($error) {
				last;
			}
		}

		# 再配置処理終了時処理
		if (!$error) {
			# 正常終了時 空フォルダ削除
			print "<p>\n空フォルダを検索しています... ";
			my @dir_path_list = do {
				# ログフォルダ リスト取得
				my @dir_paths = File::Find::Rule->directory->in($logdir);
				# ログフォルダ番号 => ログフォルダパス リストインデックス のハッシュを作り、
				# キー(ログフォルダ番号)で昇順ソート、対応するインデックスから
				# 昇順ソートしたログフォルダ リストを返す
				my %dir_number_array_index_hash = map { basename($dir_paths[$_]) => $_ } 0 .. $#dir_paths;
				map { $dir_paths[$dir_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%dir_number_array_index_hash);
			};
			print "<span style=\"color: #66cc66\">OK</span>\n</p>\n";
			foreach my $dir_path (@dir_path_list) {
				$dir_path = File::Spec->canonpath($dir_path);
				if (rmdir($dir_path)) {
					# 空フォルダで削除成功時
					print "<span style=\"color: #666633\">【空フォルダ削除】$dir_path を削除しました</span><br>\n";
				}
			}

			# 正常終了メッセージ出力
			print <<EOM;
<p style="color: #0000ff; font-weight: bold">
全ての再配置処理が正常に終了しました。
</p>
EOM
		} else {
			# エラー発生時メッセージ出力
			print <<EOM;
</div>
<div>
<p style="color: #cc0000; font-weight: bold">
再配置処理に失敗したため、ロールバック処理を行います。
ロールバック処理中のエラーは無視され、続行されます。
</p>
EOM
			# ロールバック処理
			while (my $original_path = pop(@moved_path_list)) {
				# 再配置先パス情報を取得
				my $thread_number = basename($original_path, '.cgi');
				my $replace_path = File::Spec->canonpath(get_logfolder_path($thread_number) . "/$thread_number.cgi");

				# 元のパスに配置
				print "$replace_path -> $original_path ... ";
				if (move($replace_path, $original_path)) {
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">失敗しました</span><br>\n";
				}
			}
			print <<EOM;
<p>
ロールバック処理を終了します。
</p>
EOM
		}

		# ロックファイル削除
		close($lock_fh);
		unlink($thread_log_moving_lock_path);

		# フッター出力
		print <<"EOM";
</div>
<div>
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
</div>
</body>
</html>
EOM
	} else {
		### 保存フォルダ再配置処理 実行確認表示 ###
		header();
		print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<form action="$admincgi" method="post" id="adminCGI">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="move_threadlog" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">スレッドログファイル 保存フォルダ再配置処理</h3>
<p>
全てのスレッドログファイルを適切な保存フォルダに再配置します。<br>
ログファイルの件数によっては処理に時間がかかることがあります。
</p>
<p>
また、スレッドログファイルの破損を防ぐため、
処理実行中はWebPatio全体のアクセスが拒否されますので、ご注意下さい。
</p>
<input type="submit" id="doReplace" value="再配置処理を開始する" onClick='if(confirm("本当に開始してもよろしいですか？")) { \$("#doReplace").prop("disabled", true).val("再配置処理を開始しています..."); \$("#adminCGI").submit(); } return false;'>
</form>
</body>
</html>
EOM
	}
	exit;
}

#-------------------------------------------------
#  スレッドログの閲覧、保存
#-------------------------------------------------
sub manage_log {
		my $logfile_path = get_logfolder_path($in{'file'}) . "/$in{'file'}.cgi";

		if($in{'submit'} eq 1) {
			$in{'body'} =~ s/&lt;/</g;
			$in{'body'} =~ s/&gt;/>/g;
			$in{'body'} =~ s/>>([0-9]+)/&gt;&gt;$1/g;
			open(OUT, ">", $logfile_path) || &error("Open Error: $in{'file'}.cgi");
			print OUT $in{'body'};
			close(OUT);
		}

		# スレッドログ一括読み込み
		my @log;
		my @title;
		open(my $log_fh, $logfile_path) || &error("Open Error: $in{'file'}.cgi");
		flock($log_fh, 1) || &error("Lock Error: $in{'file'}.cgi");
		$i = 1;
		while(<$log_fh>) {
			$_ =~ s/(?:\r\n|\n\r|\r|\n)$//;
			if($i eq 1) {
				push(@title, split(/<>/));
			}
			push(@log, $_);
			$i++;
		}
		close($log_fh);
		$log = join("\n", @log);

		if($in{'submit'} eq 1) {
			&success('ログを保存しました');
		}

		&header;
		print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; 掲示板">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; 管理TOP">
</form>
<h3 style="font-size:16px">
スレッド名：@title[1]<br>
スレッド番号：$in{'file'}
</h3>

<form action=\"$admincgi\" method=\"post\">
<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">
<input type=\"hidden\" name=\"mode\" value=\"admin\">
<input type=\"hidden\" name=\"file\" value=\"$in{'file'}\">
<input type=\"hidden\" name=\"action\" value=\"$in{'action'}\">
<input type=\"hidden\" name=\"cookie_id\" value=\"on\">
<input type=\"hidden\" name=\"submit\" value=\"1\">
<textarea name=\"body\" cols=\"100\" rows=\"20\">
$log
</textarea><br>
<input type=\"submit\" value=\"ログを保存\">
</form>\n</body></html>
EOM
		exit;
}