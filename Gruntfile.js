'use strict';

module.exports = function (grunt) {
    require('load-grunt-tasks')(grunt);
    require('time-grunt')(grunt);
    grunt.loadNpmTasks('grunt-bg-shell');

    grunt.initConfig({
        watch: {
            bower: {
                files: ['bower.json'],
                tasks: ['bowerInstall']
            },
            js: {
                files: ['app/scripts/{,*/}*.js'],
                options: {
                    livereload: true
                }
            },
            styles: {
                files: ['app/styles/{,*/}*.css'],
                tasks: ['newer:copy:styles']
            },
            gruntfile: {
                files: ['Gruntfile.js']
            },
            livereload: {
                options: {
                    livereload: true
                },
                files: [
                    'app/{,*/}*.html',
                    '.tmp/styles/{,*/}*.css',
                    'app/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
                ]
            },
            server: {
                files: [
                    'src/{,*/}*.py'
                ],
                tasks: [
                    'bgShell:server'
                ]
            }
        },

        clean: {
            dist: {
                files: [
                    {
                        dot: true,
                        src: [
                            '.tmp',
                            'dist/*',
                            '!dist/.git*'
                        ]
                    }
                ]
            },
            server: '.tmp'
        },

        bowerInstall: {
            app: {
                src: ['app/client.html', 'app/admin.html'],
                ignorePath: 'app/'
            }
        },

        rev: {
            dist: {
                files: {
                    src: [
                        'dist/scripts/{,*/}*.js',
                        'dist/styles/{,*/}*.css',
                        'dist/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}',
                        'dist/styles/fonts/*'
                    ]
                }
            }
        },

        useminPrepare: {
            html: ['app/client.html', 'app/admin.html'],
            options: {
                dest: 'dist',
                flow: {
                    html: {
                        steps: {
                            js: ['concat', 'uglifyjs'],
                            css: ['cssmin']
                        },
                        post: {}
                    }
                }
            }
        },

        usemin: {
            html: ['dist/{,*/}*.html'],
            css: ['dist/styles/{,*/}*.css'],
            options: {
                assetsDirs: ['dist']
            }
        },

        cssmin: {
            options: {
                root: 'app'
            }
        },

        imagemin: {
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: 'app/images',
                        src: '{,*/}*.{png,jpg,jpeg,gif}',
                        dest: 'dist/images'
                    }
                ]
            }
        },

        svgmin: {
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: 'app/images',
                        src: '{,*/}*.svg',
                        dest: 'dist/images'
                    }
                ]
            }
        },

        htmlmin: {
            dist: {
                options: {
                    collapseWhitespace: true,
                    collapseBooleanAttributes: true,
                    removeComments: true,
                    removeCommentsFromCDATA: true,
                    removeOptionalTags: true
                },
                files: [
                    {
                        expand: true,
                        cwd: 'dist',
                        src: ['*.html', 'views/{,*/}*.html'],
                        dest: 'dist'
                    }
                ]
            }
        },

        copy: {
            dist: {
                files: [
                    {
                        expand: true,
                        dot: true,
                        cwd: 'app',
                        dest: 'dist',
                        src: [
                            '*.{ico,png,txt}',
                            '*.html',
                            'views/{,*/}*.html',
                            'images/{,*/}*.{webp}',
                            'fonts/*'
                        ]
                    },
                    {
                        expand: true,
                        cwd: '.tmp/images',
                        dest: 'dist/images',
                        src: ['generated/*']
                    }
                ]
            },
            styles: {
                expand: true,
                cwd: 'app/styles',
                dest: '.tmp/styles/',
                src: '{,*/}*.css'
            }
        },

        concurrent: {
            server: [
                'copy:styles'
            ],
            test: [
                'copy:styles'
            ],
            dist: [
                'copy:styles',
                'imagemin',
                'svgmin'
            ]
        },

        bgShell: {
            server: {
                cmd: 'python src/main.py',
                bg: true
            },
            server_dist: {
                cmd: 'python src/main.py dist',
                bg: true
            }
        }
    });

    grunt.registerTask('serve', function (target) {
        if (target === 'dist') {
            return grunt.task.run(['build']);
        }
        grunt.task.run([
            'clean:server',
            'bowerInstall',
            'concurrent:server',
            target === 'dist' ? 'bgShell:server_dist' : 'bgShell:server',
            'watch'
        ]);
    });

    grunt.registerTask('build', [
        'clean:dist',
        'bowerInstall',
        'useminPrepare',
        'concurrent:dist',
        'concat',
        'copy:dist',
        'cssmin',
        'uglify',
        'rev',
        'usemin',
        'htmlmin',
        'bgShell:server_dist',
        'watch'
    ]);
};