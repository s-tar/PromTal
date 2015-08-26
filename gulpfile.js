var gulp = require('gulp');
var sass = require('gulp-sass');
var stylus = require('gulp-stylus');
var watch = require('gulp-watch');
var minifycss = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');
var gzip = require('gulp-gzip');
var concat = require('gulp-concat');
var livereload = require('gulp-livereload');
var react = require('gulp-react');

var gzip_options = {
    threshold: '1kb',
    gzipOptions: {
        level: 9
    }
};
var static_folder = './application/static';
/* Compile Our Stylus */
gulp.task('stylus', function() {
    return gulp.src(static_folder+'/stylus/*.styl')
        .pipe(concat('bundle.styl'))
        .pipe(gulp.dest(static_folder+'/stylus'))
        .pipe(stylus())
        .pipe(gulp.dest(static_folder+'/css'))
        .pipe(rename('stylus.min.css'))
        .pipe(minifycss())
        .pipe(gulp.dest(static_folder+'/css'))
        //.pipe(gzip(gzip_options))
        //.pipe(gulp.dest(static_folder+'/css'))
        .pipe(livereload());
});

/* Compile Our Css */
gulp.task('css', function() {
    return gulp.src(static_folder+'/css/*.css')
        .pipe(concat('style.min.css'))
        .pipe(gulp.dest(static_folder+'/bundle'))
        .pipe(minifycss())
        .pipe(gulp.dest(static_folder+'/bundle'))
        //.pipe(gzip(gzip_options))
        //.pipe(gulp.dest(static_folder+'/bundle'))
        .pipe(livereload());
});

/* Compile Our JSX */
gulp.task('jsx', function() {
    return gulp.src(static_folder+'/jsx/*.jsx')
        .pipe(concat('components.jsx'))
        .pipe(gulp.dest(static_folder+'/jsx'))
        .pipe(react())
        .pipe(gulp.dest(static_folder+'/js'))
        .pipe(livereload());
});

/* Compile Our JS */
gulp.task('js', function() {
    return gulp.src([
            static_folder+'/js/lib/react-with-addons.js',
            static_folder+'/js/lib/rx.all.js',
            static_folder+'/js/*.js',
            static_folder+'/js/lib/*.js',
            static_folder+'/js/lib/jquery.dataTables.min.js',
            static_folder+'/js/lib/dataTables.bootstrap.js',
            static_folder+'/js/lib/dataTables.responsive.min.js',
            '!'+static_folder+'/js/jquery.1.11.3.min.js',
            ] )
        .pipe(concat('js.bundle.js'))
        .pipe(gulp.dest(static_folder+'/bundle'))
        .pipe(uglify())
        .pipe(gulp.dest(static_folder+'/bundle'))
        .pipe(livereload());
});


/* Watch Files For Changes */
gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(static_folder+'/stylus/*.styl', ['stylus']);
    gulp.watch(static_folder+'/css/*.css', ['css']);
    gulp.watch(static_folder+'/jsx/*.jsx', ['jsx']);
    gulp.watch(static_folder+'/js/*.js', ['js']);
    gulp.watch(static_folder+'/js/lib/*.js', ['js']);
    gulp.watch('./application/templates/*').on('change', livereload.changed);

});

gulp.task('default', ['stylus', 'css', 'jsx', 'js', 'watch']);