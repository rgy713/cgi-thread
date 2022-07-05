#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� upload.pl - 2007/06/30
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

use Image::Magick;
use Digest::MD5;

#-------------------------------------------------
#  �A�b�v���[�h�t�@�C���Ǘ� ���O����
#-------------------------------------------------
# �摜�ۑ��t�H���_�Ǘ�
# ��1�����Ɉȉ��̕������^���Ă����ꂩ�̓�����s��
# get_img_folder_number_str     : �摜�ۑ��t�H���_�ԍ��̎擾 (�K�v�ɉ����ĕۑ��t�H���_�̎����쐬���s��)
# set_last_get_folder_img_saved : �Ō�Ɏ擾�����摜�ۑ��t�H���_�ԍ��̃t�H���_�ɉ摜��ۑ�������Ԃł��邱�Ƃ�ʒm���A���O�ɋL�^����
#                                 (������s��Ȃ��ꍇ�A�摜�ۑ����s���ĂȂ����̂Ƃ��ăt�H���_�ԍ��̕ω��͂Ȃ�)
my $imgfile_management = do {
    # �ŏI�擾�摜�ۑ��t�H���_ �摜�ۑ��ς݃t���O
    my $is_last_get_folder_img_saved = 1;

    # �t�H���_�ԍ��ǂݎ��
    my $img_folder_number_log_fh; # �t�H���_�ԍ����O �t�@�C���n���h��
    my $img_folder_number_str = do {
        # �t�H���_�ԍ����O�t�@�C���I�[�v��
        open($img_folder_number_log_fh, '+>>', $img_folder_number_log) || error('Open Error: Image SaveFolder Log');
        flock($img_folder_number_log_fh, 2) || error('Lock Error: Image SaveFolder Log');
        seek($img_folder_number_log_fh, 0, 0);

        # �t�H���_�ԍ���ǂݎ��
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

    # �t�H���_���摜���ǂݎ��
    my $imgfile_count_log_fh; # �t�H���_���摜�����O �t�@�C���n���h��
    my $imgfile_count = do {
        # �摜�ۑ��t�H���_���摜�����O�t�@�C�����I�[�v��
        open($imgfile_count_log_fh, '+>>', $imgfile_count_log) || error("Open Error: Image Count Log");
        flock($imgfile_count_log_fh, 2) || error("Lock Error: Image Count Log");
        seek($imgfile_count_log_fh, 0, 0);

        # �摜�ۑ��t�H���_���摜����ǂݎ��
        my $read_imgfile_count = <$imgfile_count_log_fh>;
        chomp($read_imgfile_count);
        if ($read_imgfile_count eq '') {
            # �摜�ۑ��t�H���_���摜�����O�t�@�C�� �V�K�쐬����0�Ƃ���
            truncate($imgfile_count_log_fh, 0);
            seek($imgfile_count_log_fh, 0, 0);
            print $imgfile_count_log_fh "0\n";
            0;
        } else {
            # �摜�ۑ��t�H���_���摜����ǂݎ��
            int($read_imgfile_count);
        }
    };

    # ���s�������`���閳���T�u���[�`����Ԃ�
    sub {
        if ($_[0] eq 'get_img_folder_number_str') {
            # �摜�ۑ��t�H���_���摜��������߂̏ꍇ
            if ($imgfile_count >= $max_number_of_imgfiles_in_folder) {
                # �摜�ۑ��t�H���_�ԍ��J�E���g�A�b�v���āA���O�t�@�C���ɕۑ�
                $img_folder_number_str = sprintf('%05d', int($img_folder_number_str) + 1);
                truncate($img_folder_number_log_fh, 0);
                seek($img_folder_number_log_fh, 0, 0);
                print $img_folder_number_log_fh "$img_folder_number_str\n";

                # �摜�ۑ��t�H���_���摜���J�E���g�����������āA���O�t�@�C���ɕۑ�
                $imgfile_count = 0;
                truncate($imgfile_count_log_fh, 0);
                seek($imgfile_count_log_fh, 0, 0);
                print $imgfile_count_log_fh "$imgfile_count\n";
            }

            # �摜/�T���l�C���ۑ��t�H���_��K�v�ɉ����č쐬
            if (!-d "$upldir/$img_folder_number_str") {
                mkdir("$upldir/$img_folder_number_str") || error("Create Error: Image SaveFolder");
            }
            if ($thumbnail && !-d "$thumbdir/$img_folder_number_str") {
                mkdir("$thumbdir/$img_folder_number_str") || error("Create Error: Thumbnail SaveFolder");
            }

            # �ŏI�擾�摜�ۑ��t�H���_ �摜�ۑ��ς݃t���O��������
            $is_last_get_folder_img_saved = 0;

            # �摜�ۑ��t�H���_�ԍ���Ԃ�
            return $img_folder_number_str;
        } elsif ($_[0] eq 'set_last_get_folder_img_saved') {
            if (!$is_last_get_folder_img_saved) {
                # �摜�ۑ��t�H���_���摜�����J�E���g�A�b�v
                $imgfile_count++;

                # �摜�ۑ��t�H���_���摜�������O�t�@�C���ɕۑ�
                truncate($imgfile_count_log_fh, 0);
                seek($imgfile_count_log_fh, 0, 0);
                print $imgfile_count_log_fh "$imgfile_count\n";

                # �ŏI�擾�摜�ۑ��t�H���_ �摜�ۑ��ς݃t���O���Z�b�g
                $is_last_get_folder_img_saved = 1;
            }
        }
    };
};

#-------------------------------------------------
#  �A�b�v���[�h
#-------------------------------------------------
sub upload {
    my ($no, $increase_max_num_flag, $keep_index_flag) = @_;

    my $max_num = 3;
    if ($increase_max_num_flag) {
        $max_num += $upl_increase_num;
    }

    # �A�b�v���[�h���Ȃ��摜����ɗp����AMD5�n�b�V���l��S�ď������ɂ����z����쐬
    my @ignore_img_md5hash_lc;
    foreach my $ignore_img_md5hash_str (@ignore_img_md5hash) {
        my @filtered_md5hash =
            map { lc($_) } grep { length($_) == 32 && $_ !~ qr/[^a-fA-F0-9]/ } split(qr/,/, $ignore_img_md5hash_str);
        push(@ignore_img_md5hash_lc, @filtered_md5hash);
    }

    # �A�b�v���[�h���s���摜�̔���
    my @upload_imgs;
    foreach my $i (1 .. $max_num) {
        my $orig_ex;
        # �t�@�C�������M����Ă��Ă��Ȃ��ꍇ�̓X�L�b�v
        if (!exists($fname{$i})) {
            push(@upload_imgs, undef);
            next;
        # Content-Type�w�b�_����t�@�C����ނ�F��
        } elsif ($ctype{$i} =~ m|image/gif|i) {
            $orig_ex = '.gif';
        } elsif ($ctype{$i} =~ m|image/p?jpeg|i) {
            $orig_ex = '.jpg';
        } elsif ($ctype{$i} =~ m|image/png|i) {
            $orig_ex = '.png';
        # Content-Type�ł͕s���̂Ƃ��͊g���q����t�@�C����ނ�F��
        } elsif ($fname{$i} =~ /\.gif$/) {
            $orig_ex = '.gif';
        } elsif ($fname{$i} =~ /\.jpe?g$/) {
            $orig_ex = '.jpg';
        } elsif ($fname{$i} =~ /\.png$/) {
            $orig_ex = '.png';
        } else {
            # ���Ή��t�@�C���̏ꍇ�A��z���ǉ����ăX�L�b�v
            push(@upload_imgs, []);
            next;
        }

        # �A�b�v���[�h�\�ȉ摜�t�@�C���ł��邩�ǂ����m�F
        if (!$imgex{$orig_ex}) {
            &error("�A�b�v���[�h��������Ă��Ȃ��`���̉摜�t�@\�C���ł�");
        }

        # �A�b�v���[�h�o�C�i�����擾
        my $upfile_binary = $in{"upfile$i"};

        # �}�b�N�o�C�i���r��
        if ($macbin) {
            my $len = substr($upfile_binary, 83, 4);
            $len = unpack("%N", $len);
            $upfile_binary = substr($upfile_binary, 128, $len);
        }

        # �A�b�v���[�h�摜��ǂݍ��݁A�K�v�ɉ����ĉ摜�ϊ�����ImageMagick�C���X�^���X��
        # �摜�����擾
        my ($img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5) =
            load_upload_binary($upfile_binary, $orig_ex);

        # �A�b�v���[�h���Ȃ��摜�̔���
        my $orig_md5_lc = lc($orig_md5); # �A�b�v���[�h�摜��MD5�n�b�V���l���������ɕϊ�
        if (grep { $_ eq $orig_md5_lc } @ignore_img_md5hash_lc) {
            # ��v����MD5�n�b�V���l������ꍇ�̓A�b�v���[�h���Ȃ��������̂Ƃ���
            push(@upload_imgs, undef);
            next;
        }
        if (defined($conv_md5)) {
            my $conv_md5_lc = lc($conv_md5); # �ϊ���摜��MD5�n�b�V���l���������ɕϊ�
            if (grep { $_ eq $conv_md5_lc } @ignore_img_md5hash_lc) {
                # ��v����MD5�n�b�V���l������ꍇ�̓A�b�v���[�h���Ȃ��������̂Ƃ���
                push(@upload_imgs, undef);
                next;
            }
        }

        # �A�b�v���[�h�֎~�摜�̏ꍇ�ɂ̓G���[�\�����s��
        if (grep(/$orig_md5/i, @prohibit_img_md5hash)) {
            &error("�A�b�v���[�h�ł��Ȃ��摜�ł�");
        }

        # �A�b�v���[�h���s���摜�Ƃ��āA�z��Ɋi�[
        push(@upload_imgs, [ $upfile_binary, $img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5 ]);
    }

    # ���Ή��t�@�C���A�b�v���[�h�̏ꍇ�̓G���[�\��
    my @unsupported_indexes = grep { defined($upload_imgs[$_ - 1]) && scalar(@{$upload_imgs[$_ - 1]}) == 0 } (1 .. $max_num);
    if (scalar(@unsupported_indexes) > 0) {
        error("�摜" . join("�A", @unsupported_indexes) . "���ڂ͖��Ή��t�@�C���ł��B");
    }

    # ����摜�A�b�v���[�h�֎~�@�\
    if ($prohibit_same_img_upload) {
        my %check_repeat_img = ();
        my $ii = 0;
        foreach $_ (@upload_imgs) {
            $ii += 1;
            if ($_ ne undef){
	            if (${$_}[5] ne ''){
	                if ($check_repeat_img{${$_}[5]} >= 1) {
	                    $check_repeat_img{${$_}[5]} += 1;
	                    $check_repeat_img{${$_}[5] . '_list'} = $check_repeat_img{${$_}[5] . '_list'} . '�A' . $ii;
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
	                    &error($check_repeat_img{${$_}[5].'_list'}."���ڂ͓����摜�ł��B");
	                }
	            }
            }
        }
    }

    # �摜���e�e�ʐ���
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
        error("�摜" . join("�A", @max_filesize_exceeded_img_indexes) . "���ڂ͗e�ʃI�[�o�[�ł��B");
    }

    # �A�b�v���[�h����t�@�C�����Ƃɏ���
    my ($md5hash_log, @ret) = ('');
    my $up_num = 1; # �A�b�v���[�h�ԍ�
    foreach my $upload_img_array_ref (@upload_imgs) {
        # �A�b�v���[�h���Ȃ����ڂ̓X�L�b�v
        if (!defined($upload_img_array_ref)) {
            # �ʃ��X�ҏW��ʂ���̃A�b�v���[�h�ȂǁA�ԍ������̂܂܂ɂ���K�v������ꍇ�́A
            # �����ǉ����āA�A�b�v���[�h�ԍ����J�E���g�A�b�v����
            if ($keep_index_flag) {
                push(@ret, ('', '', '', '', '', '', '', ''));
                $up_num++;
            }
            next;
        }

        # �A�b�v���[�h�摜���E�ϊ���摜�����擾
        my ($upfile_binary, $img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5) = @{$upload_img_array_ref};

        # �A�b�v���[�h�����{���A�A�b�v���[�h�t�H���_���ƃT���l�C�������擾
        my ($img_savefolder_number, $thumb_w, $thumb_h) =
            upload_file($no, $up_num, $upl_ex, $conv_binary, $upfile_binary, $img_imagick);

        # MD5�n�b�V���l���O�쐬
        $md5hash_log .= "$no-$up_num$upl_ex\n";
        $md5hash_log .= "���摜:$orig_md5\n";
        if (defined($conv_md5)) {
            $md5hash_log .= "�ϊ���:$conv_md5\n";
        }

        # �A�b�v���[�h�ԍ����J�E���g�A�b�v
        $up_num++;

        # �������ʂ�Ԃ�z��ɒǉ�
        push(@ret, ($img_savefolder_number, $upl_ex, $w, $h, $thumb_w, $thumb_h, $orig_md5, $conv_md5));
    }

    # �Ԃ�z��̃A�b�v���[�h���v�f����6�ɑ���Ȃ��ꍇ�A����Ŗ��߂�
    # ($max_num��6�����̏ꍇ�A�����ꂩ�ŃA�b�v���[�h���Ȃ��ꍇ)
    my $num_of_missing_elems = 6 - scalar(@ret);
    for (my $i = 0; $i < $num_of_missing_elems; $i++) {
        push(@ret, ('', '', '', '', '', '', '', ''));
    }

    # MD5�n�b�V���l���O�����O�t�@�C���ɒǋL
    if ($md5hash_log ne '') {
        open(my $md5hash_log_fh, '>>', $img_md5hash_log_path);
        flock($md5hash_log_fh, 2);
        print $md5hash_log_fh $md5hash_log;
        close($md5hash_log_fh);
    }

    # �Ԃ�l
    return @ret;
}

#-----------------------------------------------------------
#  �A�b�v���[�h�o�C�i���ǂݍ���
#  (�{�T�u���[�`����upload�T�u���[�`������Ă΂�܂�)
#-----------------------------------------------------------
sub load_upload_binary {
    my ($upfile_binary, $orig_ex) = @_;

    # �A�b�v���[�h�摜��MD5�n�b�V���l���v�Z
    my $orig_md5 = Digest::MD5->new()->add($upfile_binary)->hexdigest();

    # ImageMagick�����������A�A�b�v���[�h�o�C�i����ǂݍ���
    my $img_imagick = Image::Magick->new();
    $img_imagick->BlobToImage($upfile_binary);

    # GIF�A�j���ȊO�ň��k�̕K�v�����邩�ǂ���
    my $need_compress =
        ($orig_ex ne '.gif' || scalar(@{$img_imagick}) == 1) && length($upfile_binary) > $img_no_convert_filesize_max;

    # JPEG�摜��Exif�����݂��邩�ǂ���
    my $is_there_exif =
        $orig_ex eq '.jpg' && scalar(split(/(?:\r\n|\r|\n)/, $img_imagick->Get('format', '%[EXIF:*]'))) > 0;

    # �A�b�v���[�h����g���q���`
    my $upl_ex = $orig_ex;

    # JPEG�摜��Exif�����݂���ꍇ�ɁA�K�v�ɉ����Ď�����]���s���AExif���폜����
    if ($is_there_exif) {
        # ������]
        $img_imagick->AutoOrient();

        # Exif�폜
        $img_imagick->Strip();
    }

    if ($need_compress) {
        # �A�b�v�摜�ϊ����ő剡�����A�A�b�v�摜�̉������傫�����Ƀ��T�C�Y���s��
        $img_imagick->Resize(geometry => "${img_convert_resize_w}x>");

        # ����PNG�̎��A�A���t�@�`�����l��������
        if ($upl_ex eq '.png' && $img_imagick->Get('matte')) {
            compose_alpha_channel_and_color($img_imagick);
        }

        # �A�b�v���[�h����g���q���Ē�`
        $upl_ex = '.jpg';
    }

    # �摜�ϊ����Blob�����MD5�n�b�V���l�擾
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

    # �摜�T�C�Y�擾
    my ($w, $h) = $img_imagick->Get('width', 'height');

    return ($img_imagick, $upl_ex, $w, $h, $orig_md5, $conv_binary, $conv_md5);
}


#-----------------------------------------------------------
#  �t�@�C���A�b�v���[�h
#  (�{�T�u���[�`����upload�T�u���[�`������Ă΂�܂�)
#-----------------------------------------------------------
sub upload_file {
    my ($no, $i, $upl_ex, $conv_binary, $upfile_binary, $img_imagick) = @_;

    # �A�b�v�t�@�C����`
    my $img_savefolder_number = $imgfile_management->('get_img_folder_number_str');
    my $imgfile_path = "$upldir/$img_savefolder_number/$no-$i$upl_ex";

    # �A�b�v���[�h
    if (-f $imgfile_path) { error("�摜�A�b�v���s $imgfile_path"); }
    open(my $img_fh, '>', $imgfile_path) || error("�摜�A�b�v���s");
    flock($img_fh, 2) || error("�摜�A�b�v���s");
    binmode($img_fh);
    if (defined($conv_binary)) {
        print $img_fh $conv_binary;
    } else {
        print $img_fh $upfile_binary;
    }
    close($img_fh);

    # �p�[�~�b�V�����ύX
    chmod(0666, $imgfile_path);

    # �T���l�C���摜����
    my ($thumb_w, $thumb_h);
    if ($thumbnail) {
        ($thumb_w, $thumb_h) = make_thumb($img_imagick, $upl_ex, "$thumbdir/$img_savefolder_number/$no-${i}_s");
    }

    # �摜�����ۑ� �t�H���_���摜�����O�t�@�C�� �J�E���g�A�b�v�ۑ�
    $imgfile_management->('set_last_get_folder_img_saved');

    # �A�b�v���[�h�摜���E�T���l�C������Ԃ�
    return ($img_savefolder_number, $thumb_w, $thumb_h);
}

#-----------------------------------------------------------
#  �T���l�C���쐬
#-----------------------------------------------------------
sub make_thumb {
    my ($img_imagick, $upl_ex, $thumbpath_prefix) = @_;

    # �T���l�C���T�C�Y�܂Ń��T�C�Y���A�T�C�Y���擾
    $img_imagick->Resize(geometry => "${thumb_max_w}x${thumb_max_h}");
    my ($thumb_w, $thumb_h) = $img_imagick->Get('width', 'height');

    # �A�j���[�V����GIF�̎��A�����摜�𓧉߂��č���
    if ($upl_ex eq '.gif' && scalar(@{$img_imagick}) > 1) {
        my $thumb_composite_img_imagick;

        # �����摜��ǂݍ��݁A�T���l�C���T�C�Y�ɏk�����T�C�Y
        if (!-f $thumb_composite_img_path) { &error("�T���l�C���摜�A�b�v���s"); }
        if (!defined($thumb_composite_img_imagick)) {
            $thumb_composite_img_imagick = Image::Magick->new();
            $thumb_composite_img_imagick->Read($thumb_composite_img_path);
            $thumb_composite_img_imagick->Resize(geometry => "${thumb_w}x${thumb_h}>");
        }

        # �擪�R�}�摜�𔲂��o���āA����
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

    # �T���l�C���t�@�C���p�X��`
    my $thumb_path = "${thumbpath_prefix}.jpg";

    # ��������
    $img_imagick->Write(
        filename    => $thumb_path,
        compression => 'JPEG',
        quality     => $thumb_jpeg_compression_level
    );

    # �T���l�C���摜�t�@�C�� �p�[�~�b�V�����ύX
    chmod(0666, $thumb_path);

    return ($thumb_w, $thumb_h);
}

#-----------------------------------------------------------
#  �A���t�@�`�����l�� ����
#-----------------------------------------------------------
sub compose_alpha_channel_and_color {
    my ($base_img_imagick) = @_;

    my ($width, $height) = $base_img_imagick->Get('width', 'height');
    my $composite_img_imagick = Image::Magick->new(size => "${width}x${height}");
    $composite_img_imagick->Read("xc:$img_alphachannel_composite_color");
    $base_img_imagick->Composite(image => $composite_img_imagick, compose => 'DstOver');
}

1;
