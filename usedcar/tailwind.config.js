/** 株式会社delta 中古車販売LP
 *  デザイントークンは既存LP（https://delta-inc.jp/recruit-cleaning/css/style.css）から抽出した値に統一 */
module.exports = {
  content: ['./index.html', './js/**/*.js'],
  theme: {
    extend: {
      colors: {
        delta: { DEFAULT: '#0060ac', dark: '#004a85', light: '#e8f1f9' }, // プライマリ（CTA）
        ink: { DEFAULT: '#222222', 2: '#333333', 3: '#666666', 4: '#999999' },
        line: '#dddddd',
        paper: '#f8f8f8',
        error: '#c62828',
      },
      fontFamily: {
        sans: ['"Hiragino Kaku Gothic ProN"', '"Hiragino Sans"', 'Meiryo', '"Noto Sans JP"', 'sans-serif'],
        serif: ['"EB Garamond"', 'Garamond', 'serif'],
      },
    },
  },
  plugins: [],
};
