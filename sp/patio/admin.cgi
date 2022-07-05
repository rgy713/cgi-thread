#!/usr/bin/perl

#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� admin.cgi - 2007/05/06
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���肵�܎� K1.04
# 2013/03/03 �ߋ����O�̃o�O�C��
# 2009/07/04 �Ō�̃��X���폜����Ƃ��̕s�
# 2009/07/03 �ߋ����O�ɗ��Ƃ��Ƃ��ɃX���b�h�ꗗ�̃t���O�𒼂��Ă��Ȃ�����
# 2009/06/26 �ߋ����O�̃X���b�h����Ɂu�J�E�Ǘ��ҁE�e�`�p�v������͕̂ςȂ̂ŏo�Ȃ�����
# 2009/03/18 FAQ���[�h�ɒ���
# 2009/03/14 �X���b�h�쐬�������[�h�̒ǉ�
# 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V
# 2008/03/16 ���������̃o�O�C��
# 2008/02/27 �X���b�h�����@�\�𑕔��i�����ɂ͎w�背�X�ȍ~���R�s�[���ĐV�K�X���b�h�쐬�j
# 2008/01/09 �ߋ����O��<->�����̍ۂɊe�X���b�h�̃��O�ɏ�Ԃ��L�^����悤�ɕύX
# 2007/11/14 �ߋ����O��<->����
# 2007/06/23 ���b�N���Ǘ��҃��b�N�ɁA���b�N���Ƀ��X�̃^�C�g��������Ȃ��悤��
# 2007/06/10 3.2�����ɏC��

# �O���t�@�C����荞��
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
		# �����O�C�����ɁA����ID���s/����ID�F�؃t�H�[���\��
		if($in{'pass'} ne $pass){
			&error("�F�؃G���[");
		}
	} else {
		my $history_id = $cookie->('HISTORY_ID');
		if(!( grep $_ eq $history_id , @setteiti)){
			&error("�F�؃G���[");
		}
	}
} else{
	if ($in{'pass'} eq "") { &enter; }
	elsif ($in{'pass'} ne $pass) { &error("�F�؃G���["); }
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
#  ���O�����e
#-------------------------------------------------
sub file_mente {
	local($subject,$log,$top,$itop,$sub,$res,$nam,$em,$com,$da,$ho,$pw,$re,
		$sb,$na2,$key,$last_nam,$last_dat,$del,@new,@new2,@sort,@file,@del,@top);

	# ���j���[����̏���
	if ($in{'job'} eq "menu") {
		foreach ( keys(%in) ) {
			if (/^past(\d+)/) {
				$in{'past'} = $1;
				last;
			}
		}
	}

	# �����`�F�b�N
	$in{'no'} =~ s/[^0-9\0]//g;

	# index��`
	local($mylog);
	if ($in{'bakfile'}) {
		$log = $pastfile;
		$subject = "�ߋ����O";
		$mylog = "bakfile";
	} else {
		$log = $nowfile;
		$subject = "���s���O";
		$mylog = "logfile";
	}

	# �X���b�h�ꊇ�폜
	if ($in{'action'} eq "del" && $in{'no'} ne "") {

		# �폜���
		local(@del) = split(/\0/, $in{'no'});

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ڑ�
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);

		# index���폜��񒊏o
		local($top, @new);
		open(DAT,"+< $log") || &error("Open Error: $log");
		eval "flock(DAT, 2);";
		$top = <DAT> if (!$in{'bakfile'});
		while(<DAT>) {
			$flg = 0;
			local($no) = split(/<>/);
			foreach $del (@del) {
				if ($del == $no) {
					# ���O�W�J
					my $logfile_path = get_logfolder_path($del) . "/$del.cgi";
					open(DB, $logfile_path);
					while(my $db = <DB>) {
						$db =~ s/(?:\r\n|\r|\n)$//;
						my ($tim, %upl);
						($tim,$upl{1},$upl{2},$upl{3},$upl{4},$upl{5},$upl{6}) = (split(/<>/, $db))[11 .. 14, 23 .. 25];

						# �摜�폜
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
					}
					close(DB);

					# �X���b�h�폜
					unlink($logfile_path);

					# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X����A�폜���ꂽ�X���b�h�����폜
					$updatelog_db->delete_threadinfo($del);

					$flg = 1;
					last;
				}
			}
			if (!$flg) { push(@new,$_); }
		}

		# index�X�V
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ؒf
		$updatelog_db->close(0);

	# �X���b�h�̃��b�N�J��
	} elsif ($in{'action'} eq "lock" && $in{'no'} ne "" && !$in{'past'}) {

		# ���b�N���
		local(@lock) = split(/\0/, $in{'no'});

		# �X���b�h�w�b�_���X�V
		foreach (@lock) {

			local($top,@file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# �擪�L�������A�L�[�J��
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=���b�N 1=�W�� 2=�Ǘ��p
#			if ($key eq '0') { $key = 1; } else { $key = 0; }
			# �Ǘ��҃��b�N
			if ($key eq '4') { $key = 1; } else { $key = 4; }

			# �X���b�h�X�V
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index�ǂݍ���
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
				# 0=���b�N 1=�W�� 2=�Ǘ��p
				if ($lock == $no) {
				#  index�̏�ԂɊ֌W�Ȃ��A�ʃ��O�̃��b�N��Ԃɍ��킹��

				my $logfile_path = get_logfolder_path($lock) . "/$lock.cgi";
				open(IND, "+<", $logfile_path) || &error("Open Error: $lock.cgi");
				eval "flock(IND, 2);";
				$top2 = <IND>;
				close(IND);

				# �擪�L�������A�L�[�J��
				local(undef,undef,undef,$key2) = split(/<>/, $top2);

#					if ($key eq '0') { $key = 1; } else { $key = 0; }
					$_ = "$no<>$sub<>$res<>$nam<>$da<>$na2<>$key2<>$upl<>$ressub<>$restime<>$host<>";
				}
			}
			push(@new,"$_\n");
		}

		# index�X�V
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �X���b�h�̊Ǘ��҃R�����g���[�h
	} elsif ($in{'action'} eq "lock2" && $in{'no'} ne "" && !$in{'past'}) {

		# ���b�N���
		local(@lock) = split(/\0/, $in{'no'});

		# �X���b�h�w�b�_���X�V
		foreach (@lock) {

			local($top, @file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# �擪�L�������A�L�[�J��
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=���b�N 1=�W�� 2=�Ǘ��p
			if ($key != 2) { $key = 2; } else { $key = 1; }

			# �X���b�h�X�V
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index�ǂݍ���
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
					# 0=���b�N 1=�W�� 2=�Ǘ��p
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

		# index�X�V
		unshift(@new,@faq) if (@faq > 0);
		unshift(@new,@top2) if (@top2 > 0);
		unshift(@new,@top1) if (@top1 > 0);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �X���b�h�̂e�`�p���[�h �Ǘ��҃R�����g���[�h�̃p�N��
#	} elsif ($in{'action'} eq "lock2" && $in{'no'} ne "" && !$in{'past'}) {
	} elsif ($in{'action'} eq "faq" && $in{'no'} ne "" && !$in{'past'}) {

		# ���b�N���
		local(@lock) = split(/\0/, $in{'no'});

		# �X���b�h�w�b�_���X�V
		foreach (@lock) {

			local($top, @file);
			my $logfile_path = get_logfolder_path($_) . "/$_.cgi";
			open(DAT, "+<", $logfile_path) || &error("Open Error: $_.cgi");
			eval "flock(DAT, 2);";
			@file = <DAT>;

			$top = shift(@file);

			# �擪�L�������A�L�[�J��
			local($num,$sub,$res,$key) = split(/<>/, $top);

			# 0=���b�N 1=�W�� 2=�Ǘ��p 3=�e�`�p
			if ($key != 3) { $key = 3; } else { $key = 1; }

			# �X���b�h�X�V
			unshift(@file,"$num<>$sub<>$res<>$key<>\n");
			seek(DAT, 0, 0);
			print DAT @file;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# index�ǂݍ���
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
					# 0=���b�N 1=�W�� 2=�Ǘ��p 3=�e�`�p
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

		# index�X�V
		unshift(@new,@faq) if (@faq > 0);
		unshift(@new,@top2) if (@top2 > 0);
		unshift(@new,@top1) if (@top1 > 0);
		unshift(@new,$top);
		seek(DAT, 0, 0);
		print DAT @new;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �X���b�h�̉ߋ����O�� regist.cgi �̐V�K�������݃��[�`�����p�N��
	} elsif ($in{'action'} eq "archive" && $in{'no'} ne "" && $in{'logfile'}) {

	# �I���X���b�h���W�J
	local(@lock) = split(/\0/, $in{'no'});

		# index�ǂݍ���
#	local($i, $flg, $top, @new, @tmp, @top);

		local($flg,$top,@now,@past);
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
		eval "flock(DAT, 2);";
		$top = <DAT>;
		while(<DAT>) {
			$flg = 0;
#			chomp($_);
			local($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
			chomp($host); # �X���b�h�쐬�҃z�X�g�����L�^����Ă��Ȃ����t�H�[�}�b�g�̃��O�ł�\n�����邽�߁A�݊��p

			foreach $lock (@lock) {
				if ($lock == $num) {
				$flg = 1;
				last;
				}
			}
			if ($flg) {
#			unshift(@past,$_);
#			push(@past,$_);
#			�I���W�i���`���̃��O�Ή�
			chomp ($upl);
			chomp ($ressub);
			chomp ($restime);
			push(@past,"$num<>$sub<>$res<>$nam<>$date<>$na2<>-1<>$upl<>$ressub<>$restime<>$host<>\n");

			# �ߋ����O�ɗ�����X���b�h�̃t���O��ύX

		# �X���b�h�ǂݍ���
		my $logfile_path = get_logfolder_path($num) . "/$num.cgi";
		open(DAT2, "+<", $logfile_path) || &error("Open Error: $num.cgi");
		eval "flock(DAT2, 2);";
		local(@file) = <DAT2>;

		# �擪�t�@�C���𒊏o�E����
		$top2 = shift(@file);
		local($no,$sub2,$res2,undef) = split(/<>/, $top2);

		# �t���O�ύX�E�X���b�h�X�V
		unshift(@file,"$no<>$sub2<>$res2<>-1<>\n");

		seek(DAT2, 0, 0);
		print DAT2 @file;
		truncate(DAT2, tell(DAT2));
		close(DAT2);

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɁA�ߋ����O�ɗ�����X���b�h�����X�V
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($num, undef, 0);
		$updatelog_db->close(0);

			} else {
			push(@now,$_);
			}
		}

		# index�X�V
		unshift(@now,$top);
		seek(DAT, 0, 0);
		print DAT @now;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �ߋ�index�X�V
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


	# �ߋ����O�̕��A regist.cgi �̐V�K�������݃��[�`�����p�N��
	} elsif ($in{'action'} eq "extract" && $in{'no'} ne "" && $in{'bakfile'}) {

	# �I���X���b�h���W�J
	local(@lock) = split(/\0/, $in{'no'});

		# index�ǂݍ���
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
			chomp($host); # �X���b�h�쐬�҃z�X�g�����L�^����Ă��Ȃ����t�H�[�}�b�g�̃��O�ł�\n�����邽�߁A�݊��p

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

			# ���s���O�ɖ߂�X���b�h�̃t���O��ύX

		# �X���b�h�ǂݍ���
		my $logfile_path = get_logfolder_path($num) . "/$num.cgi";
		open(DAT2, "+<", $logfile_path) || &error("Open Error: $num.cgi");
		eval "flock(DAT2, 2);";
		local(@file) = <DAT2>;

		# �擪�t�@�C���𒊏o�E����
		$top2 = shift(@file);
		local($no,$sub2,$res2,undef) = split(/<>/, $top2);

		# �t���O�ύX�E�X���b�h�X�V
		unshift(@file,"$no<>$sub2<>$res2<>1<>\n");

		seek(DAT2, 0, 0);
		print DAT2 @file;
		truncate(DAT2, tell(DAT2));
		close(DAT2);

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɁA���s���O�ɕ��A����X���b�h�����X�V
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->update_threadinfo($num, undef, 1);
		$updatelog_db->close(0);

			} else {
			push(@past,$_);
			}
		}

		# �ߋ�index�X�V
#		unshift(@now,$top);
		seek(DAT, 0, 0);
		print DAT @past;
		truncate(DAT, tell(DAT));
		close(DAT);

		# ���sindex�X�V
		if (@now > 0) {
		local (@faq);
#			$i = @tmp;
#			open(DAT,"+< $pastfile") || &error("Open Error: $pastfile");
		open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
			eval "flock(DAT, 2);";
		$top = <DAT>;
			while(<DAT>) {
				local($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$host) = split(/<>/);
					# 0=���b�N 1=�W�� 2=�Ǘ��p 3=FAQ
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

	# �X���b�h�����X�L���{��
	} elsif ($in{'action'} eq "view" && $in{'no'} ne "") {

		# ���X�L���ʍ폜
		if ($in{'job'} eq "del" && $in{'no2'} ne "") {
			# �폜����z��
			my @del = split(/\0/, $in{'no2'});

			# �X���b�h�����폜�L���𒊏o
			my $logfile_path = get_logfolder_path($in{'no'}) . "/$in{'no'}.cgi";
			open(DAT, "+<", $logfile_path);
			eval "flock(DAT, 2);";
			my $top = <DAT>;
			my ($res) = (split(/<>/, $top))[2];

			# �X���b�h���O2�s��(�e���X)��背�X�ԍ����擾���A�폜�\���ǂ�������
			my $parentResNo = (split(/<>/, <DAT>))[0];
			if ($in{'no2'} =~ /^$parentResNo$/) {
				close(DAT);
				&error("�e�L���̍폜�͂ł��܂���");
			}
			seek(DAT, 0, 0);
			<DAT>;

			my (@new, $last_nam,$last_dat,$last_sub,$last_tim);
			my $res_cnt = 0; # �ŏI���X��񌈒�p���X���J�E���^ (���O�ɋL�^���郌�X����$res�����̂܂܎g�p)
			LOG_LOOP: while(<DAT>) {
				$_ =~ s/(?:\r\n|\r|\n)$//;

				my ($no,$sub,$nam,$da,$tim,%upl);
				($no,$sub,$nam,$da,$tim,$upl{1},$upl{2},$upl{3},$upl{4},$upl{5},$upl{6}) = (split(/<>/, $_))[0 .. 2, 5, 11 .. 14, 23 .. 25];

				# �폜�Ώۃ��X�̏ꍇ�͉摜���폜���ăX�L�b�v
				foreach my $del (@del) {
					if ($no == $del) {
						# �摜�폜
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
						next LOG_LOOP;
					}
				}

				# ���X�z��ɒǉ�
				push(@new, "$_\n");

				# �X���b�h���ň�ԍŌ�ɍX�V���ꂽ�L���̎������o����
				if ($tim ne 0 && $tim > $last_tim) { $last_tim = $tim; }

				# �ŏI���e�Җ��Ǝ��Ԃ��o���Ă���
				$last_nam = $nam;
				$last_dat = $da;
				# �^�C�g����
				$last_sub = $sub;
#				$last_tim = $tim;

				$res_cnt++;
			}

			$res_cnt--; # ���X�J�E���g����e���X������
			if ($res_cnt == 0) {
				# �ŏI�I�Ƀ��X���Ȃ��ꍇ
#				$last_nam = "";
#				$last_dat = "";
				$last_sub = "";
#				$last_tim = "";
			}

			# �X���b�h�X�V
			unshift(@new,$top);
			seek(DAT, 0, 0);
			print DAT @new;
			truncate(DAT, tell(DAT));
			close(DAT);

			# index���e�����ւ�
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
					# ���X���ƍŏI���e�Җ�������
					$na2 = $last_nam;
					$da  = $last_dat;
					$_ = "$no<>$sb<>$res<>$na<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>$host<>";
					push(@faq,"$_\n");
					next;
				}
				if ($in{'no'} == $no) {
					# ���X���ƍŏI���e�Җ�������
					$na2 = $last_nam;
					$da  = $last_dat;
					$_ = "$no<>$sb<>$res<>$na<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$last_tim<>$host<>";
				}
				push(@new2,"$_\n");

				# �\�[�g�p�z��
				$da =~ s/\D//g;
				push(@sort,$da);
			}

			# ���e���Ƀ\�[�g
			@new2 = @new2[sort {$sort[$b] <=> $sort[$a]} 0 .. $#sort];

			# index�X�V
			unshift(@new2,@faq) if (@faq > 0);
			unshift(@new2,@top) if (@top > 0);
			unshift(@new2,$top2) if ($in{'past'} == 0);
			seek(DAT, 0, 0);
			print DAT @new2;
			truncate(DAT, tell(DAT));
			close(DAT);

			# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɁA���X�폜��̃X���b�h���ɍX�V
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$updatelog_db->update_threadinfo($in{'no'}, $last_tim, undef);
			$updatelog_db->close(0);

		# ���X�L���ʏC��
		} elsif ($in{'job'} eq "edit" && $in{'no2'} ne "") {

			# �����I���̏ꍇ�͐擪�̂�
			($in{'no2'}) = split(/\0/, $in{'no2'});

			require $editlog;
			&edit_log("admin");

		# �X���b�h����
		} elsif ($in{'job'} eq "split" && $in{'no2'} ne "") {

			# �����ɂ͎w�肵�����X�ȍ~�ŐV�����X���b�h�����B
			# ���̃X���b�h�͂��̂܂܂Ȃ̂ŁA������͂�����ō폜�E�ҏW��������O��

			local($tops,$num,$res,$key,$i_nam2,$i_tim,$i_da,$i_ho,$flg);
			my @newt;

			# �����I���̏ꍇ�͐擪�̂ݗ��p
			($in{'no2'}) = split(/\0/, $in{'no2'});

			# �X���b�h�����폜�L���𒊏o
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
					# ������̃X���b�h�̍쐬�Җ����L�[�v
					$i_nam2 = $nam;
					$i_tim = $tim;
					$i_da= $da;
					$i_ho = $ho;
					$flg=1;
				}
				if ($flg) {
					if ($res == 1) {
						# �X���b�h������ɐe���X�ƂȂ郌�X�̏ꍇ
						$sub = $sub2; # �X���b�h�^�C�g�������X�^�C�g���Ƃ���
						$is_sage = undef; # sage�t���O���폜����
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

					# �ŏI���e�Җ��Ǝ��Ԃ��o���Ă���
					$last_nam = $nam;
					$last_dat = $da;
					# �^�C�g����
					$last_sub = $sub;
				}
			}
			close(DAT);

			# �V�K�X���b�h�쐬
			# index�t�@�C��
			local($new, $top, @new, @top, @faq);
			open(DAT,"+< $nowfile") || &error("Open Error: $nowfile");
			eval "flock(DAT, 2);";
			$top = <DAT>;
			local($no,$host2,$time2) = split(/<>/, $top);

			$new = $no + 1;

			# index�W�J
			while(<DAT>) {
				local($sub,$key) = (split(/<>/))[1,6];

#				$i++;
#				if ($sub eq $in{'sub'}) { $flg++; last; }
				if ($key == 2) { push(@top,$_); next; }
				if ($key == 3) { push(@faq,$_); next; }

# 				���̍�Ǝ��͉ߋ����O�ɗ��Ƃ��Ȃ�
#				if ($i >= $i_max) { push(@tmp,$_); }
				else { push(@new,$_); }
			}

			# �t�@�C���A�b�v
			# ���X�ɂ͉摜�����Ă��Ȃ��͂������疳��

			# ���sindex�X�V
			unshift(@new,"$new<>$sub2<>$res<>$i_nam2<>$i_da<>$last_nam<>1<><>$last_sub<>$i_tim<>$i_ho<>\n");
			unshift(@new,@faq) if (@faq > 0);
			unshift(@new,@top) if (@top > 0);
			unshift(@new,"$new<>$host2<>$time2<>\n");
			seek(DAT, 0, 0);
			print DAT @new;
			truncate(DAT, tell(DAT));
			close(DAT);

			# �X���b�h�X�V
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

			# �p�[�~�b�V�����ύX
			chmod(0666, $new_logfile_path);

			# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�ɁA������̐V�����X���b�h����ǉ�
			my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
			$updatelog_db->create_threadinfo($new, $i_tim, 1);
			$updatelog_db->close(0);
		}

		# �X���b�h���ʉ{��
		&header;
		print "<div align=\"right\">\n";
		print "<form action=\"$admincgi\" method=\"post\">\n";
		print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
		print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
		print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
		print "<input type=\"submit\" value=\"&lt;&lt; �߂�\"></form></div>\n";
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
		$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

		print "�X���b�h�� �F <b>$sub</b> [ $subject ]<hr>\n";
		print "�L�[��� : $key<br>\n";
		print "<li>�C�����͍폜��I�����ċL�����`�F�b�N���܂��B<br>\n";
		print "<li>�e�L���̍폜�͂ł��܂���B<br><br>\n";
		print "���� �F <select name=\"job\">\n";
		print "<option value=\"edit\" selected>�C��\n";
		print "<option value=\"del\">�폜\n";
		print "<option value=\"split\">����</select>\n";
		print "<input type=\"submit\" value=\"���M����\">\n";
		print "<dl>\n";

		while (<IN>) {
			chomp($_);
			local($no,$sub,$nam,$em,$com,$da,$ho,$pw,$url,$mvw,$myid,$user_id,$is_sage,$cookie_a,$history_id) = (split(/<>/))[0..10,16..19];
			$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

			if ($em) { $nam="<a href=\"mailto:$em\">$nam</a>"; }

			print "<dt><input type=\"checkbox\" name=\"no2\" value=\"$no\"> ";
			print "[<b>$no</b>] $sub <b>$nam</b>";
			if ($is_sage eq '1') { print ' [sage]'; }
			print " - $da ";
			print "�y<font color=\"$al\">$ho</font>�z\n";

			if ($authkey) { print "ID:$myid\n"; }

			if ($user_id) { print " �o�^ID:$user_id\n"; }

			if ($history_id ne '') { print " ����ID:$history_id\n"; }

			if ($cookie_a) { print " CookieA:$cookie_a\n"; }

			print "<dd>$com\n";
		}
		close(IN);

		print "</dl></form>\n</body></html>\n";
		exit;
	}

# �X���b�h���상�j���[

	&header;
	print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<h3 style="font-size:16px">�Ǘ����[�h [ $subject ]</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="$mylog" value="1">
�X���b�h���� <select name="action">
<option value="view">�ʃ����e
<option value="del">�X���폜
EOM

#	if ($in{'past'} == 0) {
# �ߋ����O�ł͂�����Ȃ��悤�Ɂi�Ƃ�����������Ă��ρj
	if ($in{'logfile'}) {
		print "<option value=\"lock\">���b�N�J��\n";
		print "<option value=\"lock2\">�Ǘ���\n";
		print "<option value=\"faq\">�e�`�p\n";
# }
#
# 	if ($in{'logfile'}) {
		print "<option value=\"archive\">�ߋ����O��\n";
	}

	if ($in{'bakfile'}) {
		print "<option value=\"extract\">���s���O��\n";
	}

	print <<EOM;
</select>
<input type="submit" value="���M����">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="400">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="4" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" nowrap>�I��</td>
  <td bgcolor="$col3" width="100%">&nbsp; �X���b�h</td>
  <td bgcolor="$col3" align="center" nowrap>���X��</td>
</tr>
EOM

	# �X���b�h�ꗗ
	open(IN,"$log") || &error("Open Error: $log");
	$top = <IN> if (!$in{'bakfile'});
	while (<IN>) {
		local($no,$sub,$res,$nam,$da,$na2,$key,$upl,$ressub,$restime) = split(/<>/);
		$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜

		print "<tr bgcolor=\"$col2\"><th bgcolor=\"$col2\">";
		print "<input type=checkbox name=\"no\" value=\"$no\"></th>";
		print "<td bgcolor=\"$col2\">";

		if ($key eq '0') {
			print "[<font color=\"$al\">���b�N��</font>] ";
		} elsif ($key == 2) {
			print "[<font color=\"$al\">�Ǘ��R�����g</font>] ";
		} elsif ($key == 3) {
			print "[<font color=\"$al\">FAQ</font>] ";
		} elsif ($key == 4) {
			print "[<font color=\"$al\">�Ǘ��҃��b�N��</font>] ";
		} elsif ($key == -1) {
			print "[<font color=\"$al\">�ߋ����O</font>] ";
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
#  �t�@�C���T�C�Y
#-------------------------------------------------
sub filesize {
	local($top,$tmp,$num,$all,$all2,$size1,$size2,$size3,$size4,$file,$file1,$file2);

	# ���s���O
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

	# �ߋ����O
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

	# �摜�e�ʎZ�o�T�u���[�`����`
	local $calc_img = sub {
		my ($ref_counter, $file_regex, $dir, $is_recursive) = @_;

		# �f�B���N�g�����ꗗ���擾
		opendir(my $dir_fh, $dir) || return;
		my @dir_list = readdir($dir_fh);
		closedir($dir_fh);

		# �w�萳�K�\���ɍ��v����t�@�C���̃T�C�Y�����v
		# �T�u�f�B���N�g���͐�p�̃��X�g�ɒǉ�
		my @subdir_list;
		my $exclude_subdir_regex = qr/^\.{1,2}$/;
		foreach my $pathname (@dir_list) {
			if (-f "$dir/$pathname" && $pathname =~ /$file_regex/) {
				${$ref_counter} += -s "$dir/$pathname";
			} elsif (-d "$dir/$pathname" && $pathname !~ /$exclude_subdir_regex/) {
				push(@subdir_list, "$dir/$pathname");
			}
		}

		# �ċA�������L���̏ꍇ�ɂ́A�T�u�f�B���N�g�����X�g���g��
		# �{�T�u���[�`�����ċA�Ăяo��
		if ($is_recursive) {
			foreach my $subdir (@subdir_list) {
				$calc_img->($ref_counter, $file_regex, $subdir, 1);
			}
		}
	};

	# �摜
	my $img = 0;
	$calc_img->(\$img, qr/^\d+-\d\.(jpg|gif|png)$/, $upldir, 1);

	# �T���l�C���摜
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
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<h3 style="font-size:16px">���O�e�ʎZ�o</h3>
<ul>
<li>�ȉ��͋L�^�t�@�C���̗e�ʁi�T�C�Y�j�ŁA�����_�ȉ��͎l�̌ܓ����܂��B
<li>���ޗ��̃t�H�[�����N���b�N����Ɗe�Ǘ���ʂɈړ����܂��B
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="280">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" rowspan="2" align="center">����</td>
  <td bgcolor="$col3" rowspan="2" width="70" align="center">�t�@�C����</td>
  <td bgcolor="$col3" colspan="3" align="center">�T�C�Y</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" width="50">���O</td>
  <td bgcolor="$col3" align="center" width="50">�摜</td>
  <td bgcolor="$col3" align="center" width="50">�T���l�C��</td>
</tr>
<tr>
  <th bgcolor="$col2">
   <form action="$admincgi" method="post">
   <input type="submit" name="logfile" value="���s���O"></th>
  <td align="right" bgcolor="$col2">$file1</td>
  <td align="right" bgcolor="$col2">$size1 KB</td>
  <td align="right" bgcolor="$col2" rowspan="2">$img KB</td>
  <td align="right" bgcolor="$col2" rowspan="2">$thumb KB</td>
</tr>
<tr bgcolor="$col2">
  <th bgcolor="$col2">
   <input type="submit" name="bakfile" value="�ߋ����O"></th>
  </th>
  <td align="right" bgcolor="$col2">$file2</td>
  <td align="right" bgcolor="$col2">$size2 KB</td>
</tr>
<tr bgcolor="$col2">
  <th bgcolor="$col2">���v</th>
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
#  ����Ǘ�
#-------------------------------------------------
sub member_mente {
	# �V�K�t�H�[��
	if ($in{'job'} eq "new") {

		&member_form();

	# �V�K���s
	} elsif ($in{'job'} eq "new2") {

		local($err);
		if (!$in{'name'}) { $err .= "���O�������͂ł�<br>\n"; }
		if ($in{'myid'} =~ /\W/) { $err .= "ID�͉p�����݂̂ł�<br>\n"; }
		if (length($in{'myid'}) < 4 || length($in{'myid'}) > 8) {
			$err .= "ID�͉p������4�`8�����ł�<br>\n";
		}
		if ($in{'mypw'} =~ /\W/) { $err .= "�p�X���[�h�͉p�����݂̂ł�<br>\n"; }
		if (length($in{'mypw'}) < 4 || length($in{'mypw'}) > 8) {
			$err .= "�p�X���[�h�͉p������4�`8�����ł�<br>\n";
		}
		if (!$in{'rank'}) { $err .= "���������I���ł�<br>\n"; }
		if ($err) { &error($err); }

		local($flg,$crypt,$id,$pw,$rank,$nam,@data);

		# ID�`�F�b�N
		$flg = 0;
		open(DAT,"+< $memfile") || &error("Open Error: $memfile");
		while(<DAT>) {
			local($id,$pw,$rank,$nam) = split(/<>/);

			if ($in{'myid'} eq $id) { $flg = 1; last; }
			push(@data,$_);
		}

		if ($flg) { &error("����ID�͊��ɓo�^�ςł�"); }

		# �p�X�Í���
		$crypt = &encrypt($in{'mypw'});

		# �X�V
		seek(DAT, 0, 0);
		print DAT "$in{'myid'}<>$crypt<>$in{'rank'}<>$in{'name'}<>\n";
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �C���t�H�[��
	} elsif ($in{'job'} eq "edit" && $in{'myid'}) {

		if ($in{'myid'} =~ /\0/) { &error("�C���I���͂P�݂̂ł�"); }

		local($flg,$id,$pw,$rank,$nam);

		$flg = 0;
		open(IN,"$memfile") || &error("Open Error: $memfile");
		while (<IN>) {
			($id,$pw,$rank,$nam) = split(/<>/);

			if ($in{'myid'} eq $id) { $flg = 1; last; }
		}
		close(IN);

		&member_form($id,$pw,$rank,$nam);

	# �C�����s
	} elsif ($in{'job'} eq "edit2") {

		local($err,$crypt);
		if (!$in{'name'}) { $err .= "���O�������͂ł�<br>\n"; }
		if ($in{'myid'} =~ /\W/) { $err .= "ID�͉p�����݂̂ł�<br>\n"; }
		if (length($in{'myid'}) < 4 || length($in{'myid'}) > 8) {
			$err .= "ID�͉p������4�`8�����ł�<br>\n";
		}
		if ($in{'chg'}) {
			if ($in{'mypw'} =~ /\W/) { $err .= "�p�X���[�h�͉p�����݂̂ł�<br>\n"; }
			if (length($in{'mypw'}) < 4 || length($in{'mypw'}) > 8) {
				$err .= "�p�X���[�h�͉p������4�`8�����ł�<br>\n";
			}

			# �p�X�Í���
			$crypt = &encrypt($in{'mypw'});

		} elsif (!$in{'chg'} && $in{'mypw'} ne "") {
			$err .= "�p�X���[�h�̋����ύX�̓`�F�b�N�{�b�N�X�ɑI�����Ă�������<br>\n";
		}
		if (!$in{'rank'}) { $err .= "���������I���ł�<br>\n"; }
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

		# �X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �폜
	} elsif ($in{'job'} eq "dele" && $in{'myid'}) {

		local($flg,@data,@del);

		# �폜���
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

		# �X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	&header;
	print <<"EOM";
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<h3 style="font-size:16px">����Ǘ�</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="hidden" name="past" value="3">
���� :
<select name="job">
<option value="new">�V�K
<option value="edit">�C��
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="280">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="3" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center" nowrap width="30">�I��</td>
  <td bgcolor="$col3" align="center" nowrap>ID</td>
  <td bgcolor="$col3" align="center" nowrap>���O</td>
  <td bgcolor="$col3" align="center" nowrap>�����N</td>
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
#  ����t�H�[��
#-------------------------------------------------
sub member_form {
	local($id,$pw,$rank,$nam) = @_;
	local($job) = $in{'job'} . '2';

	&header();
	print <<EOM;
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="submit" value="&lt; �O���">
</form>
<h3 style="font-size:16px">�o�^�t�H�[��</h3>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="member" value="1">
<input type="hidden" name="job" value="$job">
<Table border="0" cellspacing="0" cellpadding="0" width="350">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>���O</td>
  <td bgcolor="$col2"><input type="text" name="name" size="25" value="$nam"></td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>���O�C��ID</td>
  <td bgcolor="$col2">
EOM

	if ($in{'myid'}) {
		print $in{'myid'};
	} else {
		print "<input type=\"text\" name=\"myid\" size=\"10\" value=\"$id\">\n";
		print "�i�p������4�`8�����j\n";
	}

	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>�p�X���[�h</td>
  <td bgcolor="$col2">
	<input type="password" name="mypw" size="10"> �i�p������4�`8�����j
EOM

	if ($in{'myid'}) {
		print "<br><input type=\"checkbox\" name=\"chg\" value=\"1\">\n";
		print "�p�X���[�h�������ύX����ꍇ�Ƀ`�F�b�N\n";
		print "<input type=\"hidden\" name=\"myid\" value=\"$in{'myid'}\">\n";
	}

	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" align="center" nowrap>����</td>
  <td bgcolor="$col2">
EOM

	local(%rank) = (1,"�{���̂�", 2,"�{��&amp;����OK");
	foreach (1,2) {
		if ($rank == $_) {
			print "<input type=radio name=rank value=\"$_\" checked>���x��$_ ($rank{$_})<br>\n";
		} else {
			print "<input type=radio name=rank value=\"$_\">���x��$_ ($rank{$_})<br>\n";
		}
	}

	print <<EOM;
  </td>
</tr>
</table>
</Td></Tr></Table>
<p>
<input type="submit" value="���M����">
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  ���j���[���
#-------------------------------------------------
sub menu_disp {
	# �Z�b�V�����f�B���N�g���|��
	if ($authkey && $in{'login'}) {
		&ses_clean;
	}

	&header;
	print <<EOM;
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<div align="center">
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="job" value="menu">
�������e��I�����Ă��������B
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="320">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col1">
  <td bgcolor="$col3" align="center">
	�I��
  </td>
  <td bgcolor="$col3" width="100%">
	&nbsp; �������e
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="logfile" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; ���s���O�E�����e�i���X
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="bakfile" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; �ߋ����O�E�����e�i���X
  </td>
</tr>
EOM

	if ($authkey) {
		print "<tr bgcolor=\"$col2\"><td bgcolor=\"$col2\" align=\"center\">\n";
		print "<input type=\"submit\" name=\"member\" value=\"�I��\"></td>";
		print "<td bgcolor=\"$col2\" width=\"100%\">&nbsp; ����F�؂̊Ǘ�</td></tr>\n";
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="filesize" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; �t�@�C���e�ʂ̉{��
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
	&nbsp; 	<a href="$readcgi?mode=form">�V�K�X���b�h�쐬�i�X���b�h�쐬�������j</a>
  </td>
</tr>
EOM
}

	if($conf_override) {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="config_override_settings" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; ����ݒ�
  </td>
</tr>
EOM
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
	<input type="submit" name="rebuild_thread_updatelog_db" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
	&nbsp; �X���b�h�X�V�����Ǘ��f�[�^�x�[�X �č\\�z
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" align="center">
    <input type="submit" name="move_threadlog" value="�I��">
  </td>
  <td bgcolor="$col2" width="100%">
    &nbsp; �X���b�h���O�t�@�C�� �ۑ��t�H���_�Ĕz�u����
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
#  �������
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
	<div style="font-size:16px;">�y���O�̉{���z</div>
	<div style="margin:5px 0 5px 0;">����:@title[1]</div>
	<form action="$admincgi" method="post">
	    <input type="hidden" name="action" value="log">
	    <input type="hidden" name="file" value="$in{'file'}">
		<input type="hidden" name="login" value="1">
		<label id="id_pass">�p�X���[�h<label>
		<input id="id_pass" type="password" name="pass" size="16">
		<input type="submit" value=" ���M���� ">
	</form>
	<form action="$admincgi" method="post">
	    <input type="hidden" name="action" value="log">
	    <input type="hidden" name="file" value="$in{'file'}">
		<input type="hidden" name="cookie_id" value="on">
		<input type="submit" style="margin-top:5px;" value=" ����ID�ŔF�� ">
	</form>
	</td></tr>
EOM
	}
	else{
		print <<EOM;
	<tr><td align="center">
	<fieldset>
	<legend>
	���Ǘ��p�X���[�h����
	</legend>
	<form action="$admincgi" method="post">
		<input type="hidden" name="login" value="1">
		<input type="password" name="pass" size="16">
		<input type="submit" value=" �F�� "></form>
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
#  �Z�V�����f�B���N�g���|��
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
#  ����ݒ�
#-------------------------------------------------
sub config_override_settings {
	if(!$conf_override) {
		&menu_disp;
	}

	# �ݒ�l�t�@�C����������
	my $update_flg;
	if($in{'action'}) {
		$update_flg = 1;

		# �ݒ�l�`�F�b�N
		my $err;
		if(!$in{'img_default'}
			&& (
					($in{'img_width'} !~ /^\d*$/ || int($in{'img_width'})< 0)
					|| ($in{'img_height'} !~ /^\d*$/ || int($in{'img_height'})< 0)
				)
			) {
			if($thumbnail) {
				$err .= "�T���l�C��";
			} else {
				$err .= "�A�b�v���[�h";
			}
			$err .= "�摜 �\\���T�C�Y�̎w�肪����������܂���B<br>\n";
		}
		if($in{'thumb_enabled'} && !$in{'thumb_default'}
			&& (
					($in{'thumb_width'} !~ /^\d*$/ || int($in{'thumb_width'})< 0)
					|| ($in{'thumb_height'} !~ /^\d*$/ || int($in{'thumb_height'})< 0)
				)
			) {
			$err .= "�T���l�C���摜 �����T�C�Y�̎w�肪����������܂���B<br>\n";
		}
		if(!$in{'uploadext_default'}) {
			my @exts = grep { $_ =~ /^uploadext_\d*_[a-z]*$/ } sort keys %in;
			for(my $i=0; $i<$#exts+1; $i++) {
				if($in{$exts[$i]} !~ /^[01]$/) {
					$err .= "�A�b�v���[�h�\�t�@�C���g���q��POST�l���ُ�ł�<br>\n";
				}
			}
		}
		if($err) { &error($err); }

		# Shebang��$admincgi���擾
		open(ADMIN, "$admincgi") || &error("Open Error: $admincgi");
		my $shebang = <ADMIN>;
		close(ADMIN);

		# $conf_override_path�t�@�C����V�K�쐬���邩�ǂ������擾
		my $existOverrideConf = -f $conf_override_path;

		# �ݒ�l��$conf_override_path�t�@�C���ɏ�������
		open(OVERRIDECONF, "> $conf_override_path") || &error("Open Error: $conf_override_path");
		eval "flock(OVERRIDECONF, 2)";
		print OVERRIDECONF $shebang . "\n";
		print OVERRIDECONF <<"EOM";
#-------------------------------------------------------#
# WebPatio ����ݒ�Ǘ��t�@�C��                         #
#                                                       #
# ���̃t�@�C���͊Ǘ����-����ݒ�Z�N�V�����̐ݒ�ɂ�� #
# ������������Ă��邽�߁A���e��ύX���Ȃ��ŉ������B    #
#-------------------------------------------------------#

EOM
		if($in{'img_default'}) {
			undef $override_img_max_w;
			undef $override_img_max_h;
			$img_max_w = $default_img_max_w;
			$img_max_h = $default_img_max_h;
		} else {
			print OVERRIDECONF "# �A�b�v���[�h�摜�\\���T�C�Y(�T���l�C���摜�@�\\�L�����̓T���l�C���摜�\\���T�C�Y)\n";
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
				print OVERRIDECONF "# �T���l�C���摜�����T�C�Y\n";
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
			print OVERRIDECONF "# �A�b�v���[�h�摜�t�@�C���g���q\n";
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
			# �A�b�v���[�h�\�t�@�C���g���q������Ȃ��Ƃ��́A�A�b�v���[�h�@�\���~
			$image_upl = 0;
		}

		print OVERRIDECONF "1;\n";
		close(OVERRIDECONF);

		# �ݒ�t�@�C����V�K�ɍ쐬�����ꍇ�́A�p�[�~�b�V������ݒ�
		if(!$existOverrideConf) {
			chmod 0777, $conf_override_path;
		}
	}
	# �A�b�v���[�h�\�t�@�C���g���q���n�b�V������\�[�g���Ď擾
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
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="config_override_settings" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">����ݒ�@<input type="submit" value="���M����"></h3>
EOM
	if($update_flg) { print "<font color=\"red\"><b>�ݒ���X�V���܂���</b></font>\n"; }
	print <<"EOM";
<p>
<Table border="0" cellspacing="0" cellpadding="0">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="4">
<tr bgcolor="$col3">
  <th align="center">���ږ�</th>
  <th width="100%">�ݒ���e</th>
</tr>
EOM
	# �A�b�v���[�h�摜�\���T�C�Y�ݒ�(�T���l�C���摜�@�\�L�����̓T���l�C���摜�\���T�C�Y)
	print "<tr bgcolor=\"$col2\">\n";
	print "  <th align=\"center\" nowrap>";
	if($thumbnail) {
		print "�T���l�C��";
	} else {
		print "�A�b�v���[�h";
	}
	print "�摜 �\\���T�C�Y</th>\n";
	print <<"EOM";
  <td>
    <div align="center">
EOM
	print "      �� <input type=\"text\" name=\"img_width\" size=\"5\" value=\"$img_max_w\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " disabled=\"disabled\"";
	}
	print "> px&nbsp;\n";
	print "      ���� <input type=\"text\" name=\"img_height\" size=\"5\" value=\"$img_max_h\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " disabled=\"disabled\"";
	}
	print "> px\n";
	print "    </div>\n";
	print "    <input type=\"checkbox\" name=\"img_default\" value=\"1\"";
	if(!defined $override_img_max_w || !defined $override_img_max_h) {
		print " checked";
	}
	print " onchange=\"refreshDisplaySizeConfigState();\"> init.cgi�ݒ�l���g�p (�� ${default_img_max_w}px ����${default_img_max_h}px)\n";
	print <<"EOM";
  </td>
</tr>
EOM

	# �T���l�C���摜�����T�C�Y�ݒ�
	if($thumbnail) {
		print <<"EOM";
<tr bgcolor="$col2">
  <th align="center" nowrap>�T���l�C���摜 �����T�C�Y</th>
  <td>
    <div align="center">
EOM
		print "      �� <input type=\"text\" name=\"thumb_width\" size=\"5\" value=\"$thumb_max_w\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " disabled=\"disabled\"";
		}
		print "> px&nbsp;\n";
		print "      ���� <input type=\"text\" name=\"thumb_height\" size=\"5\" value=\"$thumb_max_h\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " disabled=\"disabled\"";
		}
		print "> px\n";
		print "    </div>\n";
		print "    <input type=\"checkbox\" name=\"thumb_default\" value=\"1\"";
		if(!defined $override_thumb_max_w || !defined $override_thumb_max_h) {
			print " checked";
		}
		print " onchange=\"refreshThumbnailSizeConfigState();\"> init.cgi�ݒ�l���g�p (�� ${default_thumb_max_w}px ����${default_thumb_max_h}px)\n";
		print <<"EOM";
    <input type="hidden" name="thumb_enabled" value="1">
  </td>
</tr>
EOM
	}

	# �A�b�v���[�h�\�t�@�C���g���q�I��
	print <<"EOM";
<tr bgcolor="$col2">
  <th align="center" nowrap>�A�b�v���[\�h�\\�t�@\�C���g���q</th>
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
			print "> $uc_ext�t�@\�C��";
			print "<input type=\"hidden\" name=\"uploadext_${j}_$ext\" value=\"$imgex{$sort_ext_keys[$j]}\">\n";
		}
		print "    <br>\n";
	}
	print "    <input type=\"checkbox\" name=\"uploadext_default\" value=\"1\"";
	if(!%override_imgex) {
		print " checked";
	}
	print " onchange=\"refreshExtensionConfigState();\"> init.cgi�ݒ�l���g�p\n";
	print <<"EOM";
  </td>
</tr>
</table>
</Td></Tr></Table>
EOM

	# �T���l�C���摜�@�\�������̐����T�C�Y�ݒ�l���\���̂܂ܑ��M���邽�߂�input�^�O
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
#  �X���b�h�X�V�����Ǘ��f�[�^�x�[�X �č\�z
#-------------------------------------------------
sub rebuild_thread_updatelog_db {
	my $rebuild_flg = 0;
	if($in{'action'}) {
		$rebuild_flg = 1;

		# �X���b�h�X�V�����Ǘ��f�[�^�x�[�X�č\�z����
		my $updatelog_db = ThreadUpdateLogDB->new($thread_updatelog_sqlite);
		$updatelog_db->rebuild_database($logdir);
		$updatelog_db->close(0);
	}
	&header;
	print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<form action="$admincgi" method="post" id="adminCGI">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="rebuild_thread_updatelog_db" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">�X���b�h�X�V�����Ǘ��f�[�^�x�[�X �č\\�z</h3>
EOM
	if($rebuild_flg) { print "<font color=\"red\"><b>�X���b�h�X�V�����Ǘ��f�[�^�x�[�X���č\\�z���܂���</b></font>\n"; }
	print <<"EOM";
<p>
�S�Ẵ��O�t�@�C����ǂݍ��݁A�X���b�h�X�V�����Ǘ��f�[�^�x�[�X���č\\�z���܂��B<br>
���O�t�@�C���̌����ɂ���Ă͏����Ɏ��Ԃ������邱�Ƃ�����܂��B
<p>
�܂��A�������̓f�[�^�x�[�X�ւ̃A�N�Z�X���ł��Ȃ����߁A<br>
�f�[�^�x�[�X�ւ̃A�N�Z�X�������A�X���b�h�⃌�X�̍쐬�E�ύX�E�폜�A�����@�\\�����b�N����A<br>
���p�ł��Ȃ��Ȃ�܂��̂ł����Ӊ������B
<p>
<input type="submit" id="doRebuild" value="�č\\�z�������J�n����" onClick='if(confirm("�{���ɊJ�n���Ă���낵���ł����H")) { \$("#doRebuild").prop("disabled", true).val("�č\\�z�������ł�..."); \$("#adminCGI").submit(); } return false;'>
</form>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  �X���b�h���O�t�@�C�� �ۑ��t�H���_�Ĕz�u����
#-------------------------------------------------
sub move_threadlog {
	if ($in{'action'}) {
		### �ۑ��t�H���_�Ĕz�u���� ���s ###

		# ���b�N�t�@�C���쐬�E���b�N����
		my ($lock_exist, $lock_fh) = -e $thread_log_moving_lock_path;
		open($lock_fh, '>>', $thread_log_moving_lock_path) || error("���b�N�t�@�C��($thread_log_moving_lock_path)���I�[�v���ł��܂���ł���");
		flock($lock_fh, 6) || error("�ʃv���Z�X�ōĔz�u���������s���ł���\\�������邽�߁A�������J�n�ł��܂���ł���");

		# �w�b�_�[�o��
		header("�X���b�h���O�t�@�C�� �ۑ��t�H���_�Ĕz�u����", undef, 1); # �o�b�t�@�����O�𖳌��ɂ��Đi���\�����s��
		print <<EOM;
<div>
<h1>�X���b�h���O�t�@�C�� �ۑ��t�H���_�Ĕz�u����</h1>
EOM
		if ($lock_exist) {
			print <<EOM;
<p style="color: #cc0000">
�O��̍Ĕz�u����������ɏI�����Ă��Ȃ��\\��������܂��B<br>
�ēx�A�K�؂ȃt�H���_�ւ̍Ĕz�u�������s���܂��B
</p>
EOM
		}
		print <<EOM;
</div>
<div>
<p>
�X���b�h���O�t�@�C���̕ۑ��t�H���_�Ĕz�u�������J�n���܂��B
</p>
EOM

		# �X���b�h���O�t�@�C�� ���X�g�擾
		print "<p>\n�X���b�h���O�t�@�C�������擾���Ă��܂�... ";
		my @original_path_list = do {
			# �X���b�h���O�t�@�C�� ���X�g�擾
			my @log_paths = File::Find::Rule->file->name(qr/^\d*\.cgi$/)->in($logdir);
			# �X���b�h�ԍ� => �t�@�C���p�X ���X�g�C���f�b�N�X �̃n�b�V�������A
			# �L�[(�X���b�h�ԍ�)�ŏ����\�[�g�A�Ή�����C���f�b�N�X����
			# �����\�[�g�����X���b�h���O�t�@�C�� ���X�g��Ԃ�
			my %log_number_array_index_hash = map { basename($log_paths[$_], '.cgi') => $_ } 0 .. $#log_paths;
			map { $log_paths[$log_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%log_number_array_index_hash);
		};
		print "<span style=\"color: #66cc66\">OK</span>\n</p>\n";

		# �Ĕz�u����
		my $error = 0;
		my @moved_path_list; # �Ĕz�u�ς݃t�@�C���p�X ���X�g
		while (my $original_path = File::Spec->canonpath(shift(@original_path_list))) { # �t�@�C����1���Ĕz�u����
			# �Ĕz�u��p�X�����擾
			my $thread_number = basename($original_path, '.cgi');
			my $logfolder_path = File::Spec->canonpath(get_logfolder_path($thread_number));
			my $replace_path = File::Spec->canonpath("$logfolder_path/$thread_number.cgi");

			# �Ĕz�u��p�X�������p�X�Ɠ���̏ꍇ�ɂ̓X�L�b�v
			if ($replace_path eq $original_path) {
				print "$original_path == $replace_path ... <span style=\"color: #006600\">Skip</span><br>\n";
				next;
			}

			# �Ĕz�u��t�H���_�����݂��Ȃ��ꍇ�͍쐬���� (���݂���ꍇ�͏������݌������m�F)
			if (!-e $logfolder_path) {
				print "�y�t�H���_�쐬�z $logfolder_path ���쐬���܂�... ";
				if(mkdir($logfolder_path) && chmod(0777, $logfolder_path)) {
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">���s���܂���</span><br>\n";
					$error = 1;
				}
			} else {
				if (!-w $logfolder_path) {
					print "<span style=\"color: #cc0000; font-weight:bold\">$logfolder_path �̃p�[�~�b�V�������������ݒ肳��Ă��邩�m�F���ĉ�����</span><br>\n";
					$error = 1;
				}
			}

			# �Ĕz�u
			if (!$error) {
				print "$original_path -> $replace_path ... ";
				if (move($original_path, $replace_path)) {
					push(@moved_path_list, $original_path);
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">���s���܂���</span><br>\n";
					$error = 1;
				}
			}

			# �G���[�������̓��[���o�b�N
			if ($error) {
				last;
			}
		}

		# �Ĕz�u�����I��������
		if (!$error) {
			# ����I���� ��t�H���_�폜
			print "<p>\n��t�H���_���������Ă��܂�... ";
			my @dir_path_list = do {
				# ���O�t�H���_ ���X�g�擾
				my @dir_paths = File::Find::Rule->directory->in($logdir);
				# ���O�t�H���_�ԍ� => ���O�t�H���_�p�X ���X�g�C���f�b�N�X �̃n�b�V�������A
				# �L�[(���O�t�H���_�ԍ�)�ŏ����\�[�g�A�Ή�����C���f�b�N�X����
				# �����\�[�g�������O�t�H���_ ���X�g��Ԃ�
				my %dir_number_array_index_hash = map { basename($dir_paths[$_]) => $_ } 0 .. $#dir_paths;
				map { $dir_paths[$dir_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%dir_number_array_index_hash);
			};
			print "<span style=\"color: #66cc66\">OK</span>\n</p>\n";
			foreach my $dir_path (@dir_path_list) {
				$dir_path = File::Spec->canonpath($dir_path);
				if (rmdir($dir_path)) {
					# ��t�H���_�ō폜������
					print "<span style=\"color: #666633\">�y��t�H���_�폜�z$dir_path ���폜���܂���</span><br>\n";
				}
			}

			# ����I�����b�Z�[�W�o��
			print <<EOM;
<p style="color: #0000ff; font-weight: bold">
�S�Ă̍Ĕz�u����������ɏI�����܂����B
</p>
EOM
		} else {
			# �G���[���������b�Z�[�W�o��
			print <<EOM;
</div>
<div>
<p style="color: #cc0000; font-weight: bold">
�Ĕz�u�����Ɏ��s�������߁A���[���o�b�N�������s���܂��B
���[���o�b�N�������̃G���[�͖�������A���s����܂��B
</p>
EOM
			# ���[���o�b�N����
			while (my $original_path = pop(@moved_path_list)) {
				# �Ĕz�u��p�X�����擾
				my $thread_number = basename($original_path, '.cgi');
				my $replace_path = File::Spec->canonpath(get_logfolder_path($thread_number) . "/$thread_number.cgi");

				# ���̃p�X�ɔz�u
				print "$replace_path -> $original_path ... ";
				if (move($replace_path, $original_path)) {
					print "<span style=\"color: #66cc66\">OK</span><br>\n";
				} else {
					print "<span style=\"color: #cc0000; font-weight:bold\">���s���܂���</span><br>\n";
				}
			}
			print <<EOM;
<p>
���[���o�b�N�������I�����܂��B
</p>
EOM
		}

		# ���b�N�t�@�C���폜
		close($lock_fh);
		unlink($thread_log_moving_lock_path);

		# �t�b�^�[�o��
		print <<"EOM";
</div>
<div>
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
</div>
</body>
</html>
EOM
	} else {
		### �ۑ��t�H���_�Ĕz�u���� ���s�m�F�\�� ###
		header();
		print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<form action="$admincgi" method="post" id="adminCGI">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="hidden" name="move_threadlog" value="1">
<input type="hidden" name="action" value="1">
<h3 style="font-size:16px">�X���b�h���O�t�@�C�� �ۑ��t�H���_�Ĕz�u����</h3>
<p>
�S�ẴX���b�h���O�t�@�C����K�؂ȕۑ��t�H���_�ɍĔz�u���܂��B<br>
���O�t�@�C���̌����ɂ���Ă͏����Ɏ��Ԃ������邱�Ƃ�����܂��B
</p>
<p>
�܂��A�X���b�h���O�t�@�C���̔j����h�����߁A
�������s����WebPatio�S�̂̃A�N�Z�X�����ۂ���܂��̂ŁA�����Ӊ������B
</p>
<input type="submit" id="doReplace" value="�Ĕz�u�������J�n����" onClick='if(confirm("�{���ɊJ�n���Ă���낵���ł����H")) { \$("#doReplace").prop("disabled", true).val("�Ĕz�u�������J�n���Ă��܂�..."); \$("#adminCGI").submit(); } return false;'>
</form>
</body>
</html>
EOM
	}
	exit;
}

#-------------------------------------------------
#  �X���b�h���O�̉{���A�ۑ�
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

		# �X���b�h���O�ꊇ�ǂݍ���
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
			&success('���O��ۑ����܂���');
		}

		&header;
		print <<"EOM";
<form action="$bbscgi">
<input type="submit" value="&lt; �f����">
</form>
<form action="$admincgi" method="post">
<input type="hidden" name="pass" value="$in{'pass'}">
<input type="submit" value="&lt; �Ǘ�TOP">
</form>
<h3 style="font-size:16px">
�X���b�h���F@title[1]<br>
�X���b�h�ԍ��F$in{'file'}
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
<input type=\"submit\" value=\"���O��ۑ�\">
</form>\n</body></html>
EOM
		exit;
}