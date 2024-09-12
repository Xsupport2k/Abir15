
#     cs.execute(f"""INSERT INTO {utl.countries} (id,emoji,alpha_2,name_fa,name_en,area_code,amount,is_exists,is_useable) VALUES
# (1, '🇷🇺', 'ru', 'روسیه', 'russia', 7, 5000, 1, 1),
# (2, '🇺🇦', 'ua', 'اوکراین', 'ukraine', 380, 5000, 1, 1),
# (3, '🇰🇿', 'kz', 'قزاقستان', 'kazakhstan', 7, 5000, 1, 0),
# (4, '🇨🇳', 'cn', 'چین', 'china', 86, 5000, 1, 1),
# (5, '🇵🇭', 'ph', 'فیلیپین', 'philippines', 63, 5000, 1, 1),
# (6, '🇲🇲', 'mm', 'میانمار', 'myanmar', 95, 5000, 1, 1),
# (7, '🇮🇩', 'id', 'اندونزی', 'indonesia', 62, 5000, 1, 1),
# (8, '🇲🇾', 'my', 'مالزی', 'malaysia', 60, 5000, 1, 1),
# (9, '🇰🇪', 'ke', 'کنیا', 'kenya', 254, 5000, 1, 1),
# (10, '🇹🇿', 'tz', 'تانزانیا', 'tanzania', 255, 5000, 1, 1),
# (11, '🇻🇳', 'vn', 'ویتنام', 'vietnam', 84, 5000, 1, 1),
# (12, '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'gb', 'انگلستان', 'england', 44, 5000, 1, 1),
# (13, '🇱🇻', 'lv', 'لتونی', 'latvia', 371, 5000, 1, 1),
# (14, '🇷🇴', 'ro', 'رومانی', 'romania', 40, 5000, 1, 1),
# (15, '🇪🇪', 'ee', 'استونی', 'estonia', 372, 5000, 1, 1),
# (16, '🇺🇸', 'us', 'آمریکا', 'usa', 1, 5000, 1, 1),
# (18, '🇰🇬', 'kg', 'قرقیزستان', 'kyrgyzstan', 996, 5000, 1, 1),
# (19, '🇫🇷', 'fr', 'فرانسه', 'france', 33, 5000, 1, 1),
# (21, '🇰🇭', 'kh', 'کامبوج', 'cambodia', 855, 5000, 1, 1),
# (22, '🇲🇴', 'mo', 'ماکائو', 'macau', 853, 5000, 1, 1),
# (24, '🇧🇷', 'br', 'برزیل', 'brazil', 55, 5000, 1, 1),
# (25, '🇵🇱', 'pl', 'لهستان', 'poland', 48, 5000, 1, 1),
# (26, '🇵🇾', 'py', 'پاراگوئه', 'paraguay', 595, 5000, 1, 1),
# (27, '🇳🇱', 'nl', 'هلند', 'netherlands', 31, 5000, 1, 1),
# (28, '🇱🇹', 'lt', 'لیتوانی', 'lithuania', 370, 5000, 1, 1),
# (29, '🇲🇬', 'mg', 'ماداگاسکار', 'madagascar', 261, 5000, 1, 1),
# (30, '🇨🇩', 'cd', 'کنگو', 'congo', 243, 5000, 1, 1),
# (31, '🇳🇬', 'ng', 'نیجریه', 'nigeria', 234, 5000, 1, 1),
# (32, '🇿🇦', 'za', 'آفریقای جنوبی', 'south africa', 27, 5000, 1, 1),
# (33, '🇵🇦', 'pa', 'پاناما', 'panama', 507, 5000, 1, 1),
# (34, '🇪🇬', 'eg', 'مصر', 'egypt', 20, 5000, 1, 1),
# (35, '🇮🇳', 'in', 'هند', 'india', 91, 5000, 1, 1),
# (36, '🇮🇪', 'ie', 'ایرلند', 'ireland', 353, 5000, 1, 1),
# (37, '🇨🇮', 'ci', 'ساحل عاج', 'ivory coast', 225, 5000, 1, 1),
# (39, '🇱🇦', 'la', 'لائوس', 'laos', 856, 5000, 1, 1),
# (40, '🇲🇦', 'ma', 'مراکش', 'morocco', 212, 5000, 1, 1),
# (41, '🇾🇪', 'ye', 'یمن', 'yemen', 967, 5000, 1, 1),
# (42, '🇬🇭', 'gh', 'غنا', 'ghana', 233, 5000, 1, 1),
# (43, '🇨🇦', 'ca', 'کانادا', 'canada', 1, 5000, 1, 0),
# (44, '🇦🇷', 'ar', 'آرژانتین', 'argentina', 54, 5000, 1, 1),
# (45, '🇮🇶', 'iq', 'عراق', 'iraq', 964, 5000, 1, 1),
# (46, '🇩🇪', 'de', 'آلمان', 'germany', 49, 5000, 1, 1),
# (47, '🇨🇲', 'cm', 'کامرون', 'cameroon', 237, 5000, 1, 1),
# (48, '🇹🇷', 'tr', 'ترکیه', 'turkey', 90, 5000, 1, 1),
# (49, '🇳🇿', 'nz', 'نیوزلند', 'new zealand', 64, 5000, 1, 1),
# (50, '🇦🇹', 'at', 'اتریش', 'austria', 43, 5000, 1, 1),
# (51, '🇸🇦', 'sa', 'عربستان سعودی', 'saudi arabia', 966, 5000, 1, 1),
# (52, '🇲🇽', 'mx', 'مکزیک', 'mexico', 52, 5000, 1, 1),
# (53, '🇪🇸', 'es', 'اسپانیا', 'spain', 34, 5000, 1, 1),
# (54, '🇩🇿', 'dz', 'الجزایر', 'algeria', 213, 5000, 1, 1),
# (55, '🇸🇮', 'si', 'اسلوونی', 'slovenia', 386, 5000, 1, 1),
# (56, '🇭🇷', 'hr', 'کرواسی', 'croatia', 385, 5000, 1, 1),
# (57, '🇧🇾', 'by', 'بلاروس', 'belarus', 375, 5000, 1, 1),
# (58, '🇫🇮', 'fi', 'فنلاند', 'finland', 358, 5000, 1, 1),
# (59, '🇸🇪', 'se', 'سوئد', 'sweden', 46, 5000, 1, 1),
# (60, '🇬🇪', 'ge', 'گرجستان', 'georgia', 995, 5000, 1, 1),
# (61, '🇪🇹', 'et', 'اتیوپی', 'ethiopia', 251, 5000, 1, 1),
# (62, '🇿🇲', 'zm', 'زامبیا', 'zambia', 260, 5000, 1, 1),
# (63, '🇵🇰', 'pk', 'پاکستان', 'pakistan', 92, 5000, 1, 1),
# (64, '🇹🇭', 'th', 'تایلند', 'thailand', 66, 5000, 1, 1),
# (65, '🇹🇼', 'tw', 'تایوان', 'taiwan', 886, 5000, 1, 1),
# (66, '🇵🇪', 'pe', 'پرو', 'peru', 51, 5000, 1, 1),
# (68, '🇹🇩', 'td', 'چاد', 'chad', 235, 5000, 1, 1),
# (69, '🇲🇱', 'ml', 'مالی', 'mali', 223, 5000, 1, 1),
# (70, '🇧🇩', 'bd', 'بنگلادش', 'bangladesh', 880, 5000, 1, 1),
# (71, '🇬🇳', 'gn', 'گینه', 'guinea', 224, 5000, 1, 1),
# (72, '🇱🇰', 'lk', 'سری لانکا', 'sri lanka', 94, 5000, 1, 1),
# (73, '🇺🇿', 'uz', 'ازبکستان', 'uzbekistan', 998, 5000, 1, 1),
# (74, '🇸🇳', 'sn', 'سنگال', 'senegal', 221, 5000, 1, 1),
# (75, '🇨🇴', 'co', 'کلمبیا', 'colombia', 57, 5000, 1, 1),
# (76, '🇻🇪', 've', 'ونزوئلا', 'venezuela', 58, 5000, 1, 1),
# (77, '🇭🇹', 'ht', 'هاییتی', 'haiti', 509, 5000, 1, 1),
# (78, '🇮🇷', 'ir', 'ایران', 'iran', 98, 5000, 1, 1),
# (79, '🇲🇩', 'md', 'مولداوی', 'moldova', 373, 5000, 1, 1),
# (80, '🇲🇿', 'mz', 'موزامبیک', 'mozambique', 258, 5000, 1, 1),
# (82, '🇦🇫', 'af', 'افغانستان', 'afghanistan', 93, 5000, 1, 1),
# (83, '🇺🇬', 'ug', 'اوگاندا', 'uganda', 256, 5000, 1, 1),
# (84, '🇦🇺', 'au', 'استرالیا', 'australia', 61, 5000, 1, 1),
# (85, '🇦🇪', 'ae', 'امارات', 'uae', 971, 5000, 1, 1),
# (86, '🇨🇱', 'cl', 'شیلی', 'chile', 56, 5000, 1, 1),
# (88, '🇳🇵', 'np', 'نپال', 'nepal', 977, 5000, 1, 1),
# (89, '🇩🇯', 'dj', 'جیبوتی', 'djibouti', 253, 5000, 1, 1),
# (91, '🇳🇮', 'ni', 'نیکاراگوئه', 'nicaragua', 505, 5000, 1, 1),
# (94, '🇦🇴', 'ao', 'آنگولا', 'angola', 244, 5000, 1, 1),
# (95, '🇧🇴', 'bo', 'بولیوی', 'bolivia', 591, 5000, 1, 1),
# (96, '🇺🇾', 'uy', 'اروگوئه', 'uruguay', 598, 5000, 1, 1),
# (97, '🇪🇨', 'ec', 'اکوادور', 'ecuador', 593, 5000, 1, 1),
# (98, '🇮🇹', 'it', 'ایتالیا', 'italy', 39, 5000, 1, 1),
# (99, '🇬🇹', 'gt', 'گواتمالا', 'guatemala', 502, 5000, 1, 1),
# (100, '🇹🇳', 'tn', 'تونس', 'tunisia', 216, 5000, 1, 1),
# (101, '🇭🇺', 'hu', 'مجارستان', 'hungary', 36, 5000, 1, 1),
# (102, '🇰🇼', 'kw', 'کویت', 'kuwait', 965, 5000, 1, 1),
# (103, '🇦🇿', 'az', 'آذربایجان', 'azerbaijan', 994, 5000, 1, 1),
# (104, '🇸🇩', 'sd', 'سودان', 'sudan', 249, 5000, 1, 1),
# (105, '🇷🇼', 'rw', 'رواندا', 'rwanda', 250, 5000, 1, 1),
# (108, '🇨🇷', 'cr', 'کاستاریکا', 'costa rica', 506, 5000, 1, 1),
# (109, '🇭🇳', 'hn', 'هندوراس', 'honduras', 504, 5000, 1, 1),
# (113, '🇹🇲', 'tm', 'ترکمنستان', 'turkmenistan', 993, 5000, 1, 1),
# (114, '🇸🇾', 'sy', 'سوریه', 'syria', 963, 5000, 1, 1),
# (117, '🇵🇷', 'pr', 'پورتوریکو', 'puerto rico', 1, 5000, 1, 0),
# (118, '🇧🇬', 'bg', 'بلغارستان', 'bulgaria', 359, 5000, 0, 1),
# (119, '🇧🇪', 'be', 'بلژیک', 'belgium', 32, 5000, 1, 1),
# (120, '🇨🇿', 'cz', 'چک', 'czech', 420, 5000, 1, 1),
# (121, '🇸🇰', 'sk', 'اسلواکی', 'slovakia', 421, 5000, 1, 1),
# (122, '🇳🇴', 'no', 'نروژ', 'norway', 47, 5000, 1, 1),
# (123, '🇵🇹', 'pt', 'پرتغال', 'portugal', 351, 5000, 1, 1),
# (124, '🇱🇺', 'lu', 'لوکزامبورگ', 'luxembourg', 352, 5000, 1, 1),
# (125, '🇦🇲', 'am', 'ارمنستان', 'armenia', 374, 5000, 1, 1),
# (126, '🇯🇲', 'jm', 'جامائیکا', 'jamaica', 1876, 5000, 1, 1),
# (129, '🇯🇴', 'jo', 'اردن', 'jordan', 962, 5000, 1, 1),
# (130, '🇴🇲', 'om', 'عمان', 'oman', 968, 5000, 1, 1),
# (131, '🇧🇭', 'bh', 'بحرین', 'bahrain', 973, 5000, 1, 1),
# (132, '🇶🇦', 'qa', 'قطر', 'qatar', 974, 5000, 1, 1),
# (133, '🇲🇳', 'mn', 'مغولستان', 'mongolia', 976, 5000, 1, 1),
# (134, '🇲🇻', 'mv', 'مالدیو', 'maldives', 960, 5000, 1, 1),
# (135, '🇱🇾', 'ly', 'لیبی', 'libya', 218, 5000, 1, 1),
# (137, '🇧🇫', 'bf', 'بورکینافاسو', 'burkina faso', 226, 5000, 1, 1),
# (139, '🇧🇯', 'bj', 'بنین', 'benin', 229, 5000, 1, 1),
# (141, '🇸🇴', 'so', 'سومالی', 'somalia', 252, 5000, 0, 1),
# (142, '🇿🇼', 'zw', 'زیمبابوه', 'zimbabwe', 263, 5000, 1, 1),
# (148, '🇨🇭', 'ch', 'سوئیس', 'switzerland', 41, 5000, 0, 1),
# (150, '🇧🇧', 'bb', 'باربادوس', 'barbados', 1246, 5000, 0, 1),
# (155, '🇸🇬', 'sg', 'سنگاپور', 'singapore', 65, 5000, 1, 1),
# (156, '🇹🇯', 'tj', 'تاجیکستان', 'tajikistan', 992, 5000, 0, 1),
# (159, '🇨🇾', 'cy', 'قبرس', 'cyprus', 357, 5000, 0, 1);""")
# except:
#     pass