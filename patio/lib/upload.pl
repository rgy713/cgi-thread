#┌─────────────────────────────────
#│ [ WebPatio ]
#│ upload.pl - 2007/06/30
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

use Image::Magick;
use Digest::MD5;

#-------------------------------------------------
#  アップロードファイル管理 事前準備
#-------------------------------------------------
# 画像保存フォルダ管理
# 第1引数に以下の文字列を与えていずれかの動作を行う
# get_img_folder_number_str     : 画像保存フォルダ番号の取得 (必要に応じて保存フォルダの自動作成を行う)
# set_last_get_folder_img_saved : 最後に取得した画像保存フォルダ番号のフォルダに画像を保存した状態であることを通知し、ログに記録する
#                                 (これを行わない場合、画像保存が行われてないものとしてフォルダ番号の変化はない)
my $imgfile_management = do {
    # 最終取得画像保存フォルダ 画像保存済みフラグ
    my $is_last_get_folder_img_saved = 1;

    # フォルダ番号読み取り
    my $img_folder_number_log_fh; # フォルダ番号ログ ファイルハンドル
    my $img_folder_number_str = do {
        # フォルダ番号ログファイルオープン
        open($img_folder_number_log_fh, '+>>', $img_folder_number_log) || error('Open Error: Image SaveFolder Log');
        flock($img_folder_number_log_fh, 2) || error('Lock Error: Image SaveFolder Log');
        seek($img_folder_number_log_fh, 0, 0);

        # フォルダ番号を読み取り
        my $read_line = <$img_folder_number_log_fh>;
        chomp($read_line);
        if ($read_line ne '') {
            $read_line;
        } else {
            truncate($img_folder_number_log_fh, 0);
            seek($img_folder_number_log_fh, 0, 0);
            print $img_folder_number_log_fh "00002\n";
            '00002';
        }
    };

    # フォルダ内画像数読み取り
    my $imgfile_count_log_fh; # フォルダ内画像数ログ ファイルハンドル
    my $imgfile_count = do {
        # 画像保存フォルダ内画像数ログファイルをオープン
        open($imgfile_count_log_fh, '+>>', $imgfile_count_log) || error("Open Error: Image Count Log");
        flock($imgfile_count_log_fh, 2) || error("Lock Error: Image Count Log");
        seek($imgfile_count_log_fh, 0, 0);

        # 画像保存フォルダ内画像数を読み取り
        my $read_imgfile_count = <$imgfile_count_log_fh>;
        chomp($read_imgfile_count);
        if ($read_imgfile_count eq '') {
            # 画像保存フォルダ内画像数ログファイル 新規作成時は0とする
            truncate($imgfile_count_log_fh, 0);
            seek($imgfile_count_log_fh, 0, 0);
            print $imgfile_count_log_fh "0\n";
            0;
        } else {
            # 画像保存フォルダ内画像数を読み取る
            int($read_imgfile_count);
        }
    };

    # 実行処理を定義する無名サブルーチンを返す
    sub {
        if ($_[0] eq 'get_img_folder_number_str') {
            # 画像保存フォルダ内画像上限数超過の場合
            if ($imgfile_count >= $max_number_of_imgfiles_in_folder) {
                # 画像保存フォルダ番号カウントアップして、ログファイルに保存
                $img_folder_number_str = sprintf('%05d', int($img_folder_number_str) + 1);
                truncate($img_folder_number_log_fh, 0);
                seek($img_folder_number_log_fh, 0, 0);
                print $img_folder_number_log_fh "$img_folder_number_str\n";

                # 画像保存フォルダ内画像数カウントを初期化して、ログファイルに保存
                $imgfile_count = 0;
                truncate($imgfile_count_log_fh, 0);
                seek($imgfile_count_log_fh, 0, 0);
                print $imgfile_count_log_fh "$imgfile_count\n";
            }

            # 画像/サムネイル保存フォルダを必要に応じて作成
            if (!-d "$upldir/$img_folder_number_str") {
                mkdir("$upldir/$img_folder_number_str") || error("Create Error: Image SaveFolder");
            }
            if ($thumbnail && !-d "$thumbdir/$img_folder_number_str") {
                mkdir("$thumbdir/$img_folder_number_str") || error("Create Error: Thumbnail SaveFolder");
            }

            # 最終取得画像保存フォルダ 画像保存済みフラグを初期化
            $is_last_get_folder_img_saved = 0;

            # 画像保存フォルダ番号を返す
            return $img_folder_number_str;
        } elsif ($_[0] eq 'set_last_get_folder_img_saved') {
            if (!$is_last_get_folder_img_saved) {
                # 画像保存フォルダ内画像数をカウントアップ
                $imgfile_count++;

                # 画像保存フォルダ内画像数をログファイルに保存
                truncate($imgfile_count_log_fh, 0);
                seek($imgfile_count_log_fh, 0, 0);
                print $imgfile_count_log_fh "$imgfile_count\n";

                # 最終取得画像保存フォルダ 画像保存済みフラグをセット
                $is_last_get_folder_img_saved = 1;
            }
        }
    };
};

#-------------------------------------------------
#  アップロード
#-------------------------------------------------
sub upload {
    my ($no, $increase_max_num_flag, $keep_index_flag) = @_;

    my $max_num = 3;
    if ($increase_max_num_flag) {
        $max_num += $upl_increase_num;
    }

    # アップロードしない画像判定に用いる、MD5ハッシュ値を全て小文字にした配列を作成
    my @ignore_img_md5hash_lc;
    foreach my $ignore_img_md5hash_str (@ignore_img_md5hash) {
        my @filtered_md5hash =
            map { lc($_) } grep { length($_) == 32 && $_ !~ qr/[^a-fA-F0-9]/ } split(qr/,/, $ignore_img_md5hash_str);
        push(@ignore_img_md5hash_lc, @filtered_md5hash);
    }

    # アップロードを行う画像の判定
    my @upload_imgs;
    foreach my $i (1 .. $max_num) {
        my $orig_ex;
        # ファイルが送信されてきていない場合はスキップ
        if (!exists($fname{$i})) {
            push(@upload_imgs, undef);
            next;
        # Content-Typeヘッダからファイル種類を認識
        } elsif ($ctype{$i} =~ m|image/gif|i) {
            $orig_ex = '.gif';
        } elsif ($ctype{$i} =~ m|image/p?jpeg|i) {
            $orig_ex = '.jpg';
        } elsif ($ctype{$i} =~ m|image/png|i) {
            $orig_ex = '.png';
        # Content-Typeでは不明のときは拡張子からファイル種類を認識
        } elsif ($fname{$i} =~ /\.gif$/) {
            $orig_ex = '.gif';
        } elsif ($fname{$i} =~ /\.jpe?g$/) {
            $orig_ex = '.jpg';
        } elsif ($fname{$i} =~ /\.png$/) {
            $orig_ex = '.png';
        } else {
            # 未対応ファイルの場合、空配列を追加してスキップ
            push(@upload_imgs, []);
            next;
        }

        # アップロード可能な画像ファイルであるかどうか確認
        if (!$imgex{$orig_ex}) {
            &error("アップロードが許可されていない形式の画像ファ\イルです");
        }

        # アップロードバイナリを取得
        my $upfile_binary = $in{"upfile$i"};

        # マックバイナリ排除
        if ($macbin) {
            my $len = substr($upfile_binary, 83, 4);
            $len = unpack("%N", $len);
            $upfile_binary = substr($upfile_binary, 128, $len);
        }

        # アップロード画像を読み込み、必要に応じて画像変換したImageMagickインスタンスと
        # 画像情報を取得
        my ($img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5) =
            load_upload_binary($upfile_binary, $orig_ex);

        # アップロードしない画像の判定
        my $orig_md5_lc = lc($orig_md5); # アップロード画像のMD5ハッシュ値を小文字に変換
        if (grep { $_ eq $orig_md5_lc } @ignore_img_md5hash_lc) {
            # 一致するMD5ハッシュ値がある場合はアップロードがなかったものとする
            push(@upload_imgs, undef);
            next;
        }
        if (defined($conv_md5)) {
            my $conv_md5_lc = lc($conv_md5); # 変換後画像のMD5ハッシュ値を小文字に変換
            if (grep { $_ eq $conv_md5_lc } @ignore_img_md5hash_lc) {
                # 一致するMD5ハッシュ値がある場合はアップロードがなかったものとする
                push(@upload_imgs, undef);
                next;
            }
        }

        # アップロード禁止画像の場合にはエラー表示を行う
        if (grep(/$orig_md5/i, @prohibit_img_md5hash)) {
            &error("アップロードできない画像です");
        }

        # アップロードを行う画像として、配列に格納
        push(@upload_imgs, [ $upfile_binary, $img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5 ]);
    }

    # 未対応ファイルアップロードの場合はエラー表示
    my @unsupported_indexes = grep { defined($upload_imgs[$_ - 1]) && scalar(@{$upload_imgs[$_ - 1]}) == 0 } (1 .. $max_num);
    if (scalar(@unsupported_indexes) > 0) {
        error("画像" . join("、", @unsupported_indexes) . "枚目は未対応ファイルです。");
    }

    # 同一画像アップロード禁止機能
    if ($prohibit_same_img_upload) {
        my %check_repeat_img = ();
        my $ii = 0;
        foreach $_ (@upload_imgs) {
            $ii += 1;
            if ($_ ne undef){
	            if (${$_}[5] ne ''){
	                if ($check_repeat_img{${$_}[5]} >= 1) {
	                    $check_repeat_img{${$_}[5]} += 1;
	                    $check_repeat_img{${$_}[5] . '_list'} = $check_repeat_img{${$_}[5] . '_list'} . '、' . $ii;
	                }
	                else {
	                    $check_repeat_img{${$_}[5]} = 1;
	                    $check_repeat_img{${$_}[5] . '_list'} = $ii;
	                }
	            }
            }
        }

        foreach $_ (@upload_imgs) {
        	if ($_ ne undef){
	            if(${$_}[5] ne ''){
	                if ($check_repeat_img{${$_}[5]} > 1){
	                    &error($check_repeat_img{${$_}[5].'_list'}."枚目は同じ画像です。");
	                }
	            }
            }
        }
    }

    # 画像投稿容量制限
    my @max_filesize_exceeded_img_indexes;
    for (my $i = 0; $i < $max_num; $i++) {
        if (!defined($upload_imgs[$i])) {
            next;
        }
        my ($upfile_binary, $upl_ex) = @{$upload_imgs[$i]}[0, 2];
        my $upfile_size = length($upfile_binary);
        my $limit_filesize = $upl_ex eq '.gif' ? $maxdata_gif : $maxdata;

        if ($upfile_size > $limit_filesize) {
            push(@max_filesize_exceeded_img_indexes, ($i + 1));
        }
    }
    if (scalar(@max_filesize_exceeded_img_indexes) > 0) {
        error("画像" . join("、", @max_filesize_exceeded_img_indexes) . "枚目は容量オーバーです。");
    }

    # アップロードするファイルごとに処理
    my ($md5hash_log, @ret) = ('');
    my $up_num = 1; # アップロード番号
    foreach my $upload_img_array_ref (@upload_imgs) {
        # アップロードがない項目はスキップ
        if (!defined($upload_img_array_ref)) {
            # 個別レス編集画面からのアップロードなど、番号をそのままにする必要がある場合は、
            # 空情報を追加して、アップロード番号をカウントアップする
            if ($keep_index_flag) {
                push(@ret, ('', '', '', '', '', '', '', ''));
                $up_num++;
            }
            next;
        }

        # アップロード画像情報・変換後画像情報を取得
        my ($upfile_binary, $img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5) = @{$upload_img_array_ref};

        # アップロードを実施し、アップロードフォルダ情報とサムネイル情報を取得
        my ($img_savefolder_number, $thumb_w, $thumb_h) =
            upload_file($no, $up_num, $upl_ex, $conv_binary, $upfile_binary, $img_imagick);

        # MD5ハッシュ値ログ作成
        $md5hash_log .= "$no-$up_num$upl_ex\n";
        $md5hash_log .= "元画像:$orig_md5\n";
        if (defined($conv_md5)) {
            $md5hash_log .= "変換後:$conv_md5\n";
        }

        # アップロード番号をカウントアップ
        $up_num++;

        # 処理結果を返り配列に追加
        push(@ret, ($img_savefolder_number, $upl_ex, $w, $h, $thumb_w, $thumb_h, $orig_md5, $conv_md5));
    }

    # 返り配列のアップロード情報要素数が6に足らない場合、空情報で埋める
    # ($max_numが6未満の場合、いずれかでアップロードがない場合)
    my $num_of_missing_elems = 6 - scalar(@ret);
    for (my $i = 0; $i < $num_of_missing_elems; $i++) {
        push(@ret, ('', '', '', '', '', '', '', ''));
    }

    # MD5ハッシュ値ログをログファイルに追記
    if ($md5hash_log ne '') {
        open(my $md5hash_log_fh, '>>', $img_md5hash_log_path);
        flock($md5hash_log_fh, 2);
        print $md5hash_log_fh $md5hash_log;
        close($md5hash_log_fh);
    }

    # 返り値
    return @ret;
}

#-----------------------------------------------------------
#  アップロードバイナリ読み込み
#  (本サブルーチンはuploadサブルーチンから呼ばれます)
#-----------------------------------------------------------
sub load_upload_binary {
    my ($upfile_binary, $orig_ex) = @_;

    # アップロード画像のMD5ハッシュ値を計算
    my $orig_md5 = Digest::MD5->new()->add($upfile_binary)->hexdigest();

    # ImageMagickを初期化し、アップロードバイナリを読み込み
    my $img_imagick = Image::Magick->new();
    $img_imagick->BlobToImage($upfile_binary);

    # GIFアニメ以外で圧縮の必要があるかどうか
    my $need_compress =
        ($orig_ex ne '.gif' || scalar(@{$img_imagick}) == 1) && length($upfile_binary) > $img_no_convert_filesize_max;

    # JPEG画像でExifが存在するかどうか
    my $is_there_exif =
        $orig_ex eq '.jpg' && scalar(split(/(?:\r\n|\r|\n)/, $img_imagick->Get('format', '%[EXIF:*]'))) > 0;

    # アップロードする拡張子を定義
    my $upl_ex = $orig_ex;

    # JPEG画像でExifが存在する場合に、必要に応じて自動回転を行い、Exifを削除する
    if ($is_there_exif) {
        # 自動回転
        $img_imagick->AutoOrient();

        # Exif削除
        $img_imagick->Strip();
    }

    if ($need_compress) {
        # アップ画像変換時最大横幅より、アップ画像の横幅が大きい時にリサイズを行う
        $img_imagick->Resize(geometry => "${img_convert_resize_w}x>");

        # 透過PNGの時、アルファチャンネルを合成
        if ($upl_ex eq '.png' && $img_imagick->Get('matte')) {
            compose_alpha_channel_and_color($img_imagick);
        }

        # アップロードする拡張子を再定義
        $upl_ex = '.jpg';
    }

    # 画像変換後のBlobおよびMD5ハッシュ値取得
    my ($conv_binary, $conv_md5);
    if ($is_there_exif || $need_compress) {
        if ($need_compress) {
            $conv_binary = $img_imagick->ImageToBlob(
                compression => 'JPEG',
                magick      => 'jpg',
                quality     => $img_jpeg_compression_level
            );
        } else {
            $conv_binary = $img_imagick->ImageToBlob();
        }
        $conv_md5 = Digest::MD5->new()->add($conv_binary)->hexdigest();
    }

    # 画像サイズ取得
    my ($w, $h) = $img_imagick->Get('width', 'height');

    return ($img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5);
}


#-----------------------------------------------------------
#  ファイルアップロード
#  (本サブルーチンはuploadサブルーチンから呼ばれます)
#-----------------------------------------------------------
sub upload_file {
    my ($no, $i, $upl_ex, $conv_binary, $upfile_binary, $img_imagick) = @_;

    # アップファイル定義
    my $img_savefolder_number = $imgfile_management->('get_img_folder_number_str');
    my $imgfile_path = "$upldir/$img_savefolder_number/$no-$i$upl_ex";

    # アップロード
    if (-f $imgfile_path) { error("画像アップ失敗 $imgfile_path"); }
    open(my $img_fh, '>', $imgfile_path) || error("画像アップ失敗");
    flock($img_fh, 2) || error("画像アップ失敗");
    binmode($img_fh);
    if (defined($conv_binary)) {
        print $img_fh $conv_binary;
    } else {
        print $img_fh $upfile_binary;
    }
    close($img_fh);

    # パーミッション変更
    chmod(0666, $imgfile_path);

    # サムネイル画像生成
    my ($thumb_w, $thumb_h);
    if ($thumbnail) {
        ($thumb_w, $thumb_h) = make_thumb($img_imagick, $upl_ex, "$thumbdir/$img_savefolder_number/$no-${i}_s");
    }

    # 画像分割保存 フォルダ内画像数ログファイル カウントアップ保存
    $imgfile_management->('set_last_get_folder_img_saved');

    # アップロード画像情報・サムネイル情報を返す
    return ($img_savefolder_number, $thumb_w, $thumb_h);
}

#-----------------------------------------------------------
#  サムネイル作成
#-----------------------------------------------------------
sub make_thumb {
    my ($img_imagick, $upl_ex, $thumbpath_prefix) = @_;

    # サムネイルサイズまでリサイズし、サイズを取得
    $img_imagick->Resize(geometry => "${thumb_max_w}x${thumb_max_h}");
    my ($thumb_w, $thumb_h) = $img_imagick->Get('width', 'height');

    # アニメーションGIFの時、合成画像を透過して合成
    if ($upl_ex eq '.gif' && scalar(@{$img_imagick}) > 1) {
        my $thumb_composite_img_imagick;

        # 合成画像を読み込み、サムネイルサイズに縮小リサイズ
        if (!-f $thumb_composite_img_path) { &error("サムネイル画像アップ失敗"); }
        if (!defined($thumb_composite_img_imagick)) {
            $thumb_composite_img_imagick = Image::Magick->new();
            $thumb_composite_img_imagick->Read($thumb_composite_img_path);
            $thumb_composite_img_imagick->Resize(geometry => "${thumb_w}x${thumb_h}>");
        }

        # 先頭コマ画像を抜き出して、合成
        $img_imagick = $img_imagick->[0];
        $img_imagick->Composite(
            image   => $thumb_composite_img_imagick,
            compose => 'Dissolve',
            gravity => 'Center',
            opacity => 655.35 * ${thumb_composite_img_opacity}
        );
        # magic number "655.35" is workaround for "opacity" argument bug in PerlMagick.
        # http://www.imagemagick.org/discourse-server/viewtopic.php?t=4036
    }

    # サムネイルファイルパス定義
    my $thumb_path = "${thumbpath_prefix}.jpg";

    # 書き込み
    $img_imagick->Write(
        filename    => $thumb_path,
        compression => 'JPEG',
        quality     => $thumb_jpeg_compression_level
    );

    # サムネイル画像ファイル パーミッション変更
    chmod(0666, $thumb_path);

    return ($thumb_w, $thumb_h);
}

#-----------------------------------------------------------
#  アルファチャンネル 合成
#-----------------------------------------------------------
sub compose_alpha_channel_and_color {
    my ($base_img_imagick) = @_;

    my ($width, $height) = $base_img_imagick->Get('width', 'height');
    my $composite_img_imagick = Image::Magick->new(size => "${width}x${height}");
    $composite_img_imagick->Read("xc:$img_alphachannel_composite_color");
    $base_img_imagick->Composite(image => $composite_img_imagick, compose => 'DstOver');
}

1;
