'use strict';

const gulp = require('gulp');
const autoprefixer = require('gulp-autoprefixer');
const imagemin = require('gulp-imagemin');
const imageResize = require('gulp-image-resize');
const minifyCSS = require('gulp-csso');
const sass = require('gulp-sass');


const css = () => {
  return gulp.src('src/static/sass/main.scss')
    .pipe(
      sass(
        {
          includePaths: [
            'node_modules/normalize.css/'
          ]
        }
      ).on('error', sass.logError)
    )
    .pipe(autoprefixer())
    .pipe(minifyCSS())
    .pipe(gulp.dest('src/static/css'));
};

const img = () => {
  return gulp.src('src/static/img_src/*')
    .pipe(imageResize({
      width : 1260,
      upscale : false
    }))
    .pipe(imagemin())
    .pipe(gulp.dest('src/static/img'))
};

const watchSass = () => {
  gulp.watch('./src/static/sass/**/*.scss', css);
};

const watch = gulp.series(gulp.parallel(css, img), watchSass);

exports.img = img;
exports.css = css;
exports.watch = watch;

exports.default = gulp.parallel(watch);
