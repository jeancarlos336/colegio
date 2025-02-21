# Definir los menús específicos para cada rol con la estructura correcta
MENUS = {
        'ADMIN': [
            {
                'label': 'Usuarios',
                'url': 'lista_usuarios',  # Este nombre coincide con tu urls.py
                'icon': 'fa-users',
                'submenu': [
                    {'name': 'Listar Usuarios', 'url': 'lista_usuarios'},  # '/usuarios/listar/'
                    {'name': 'Crear Usuario', 'url': 'crear_usuario'},     # '/usuarios/crear/'
                ]
            },
            {
                'label': 'Sedes',
                'url': 'lista_sedes',  # Agregando otra sección del menú basada en tus URLs
                'icon': 'fa-building',
                'submenu': [
                    {'name': 'Listar Sedes', 'url': 'lista_sedes'},
                    {'name': 'Crear Sede', 'url': 'crear_sede'},
                ]
            },
            {
                'label': 'Cursos',
                'url': 'lista_cursos',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Cursos', 'url': 'lista_cursos'},
                    {'name': 'Crear Curso', 'url': 'crear_curso'},
                ]
            },
            {
                'label': 'Asignaturas',
                'url': 'lista_asignaturas',
                'icon': 'fa fa-bookmark',
                'submenu': [
                    {'name': 'Listar Asignatura', 'url': 'lista_asignaturas'},
                    {'name': 'Crear Asignatura', 'url': 'crear_asignatura'},
                ]
            },
            {
                'label': 'Dias',
                'url': 'lista_dias',
                'icon': 'fa fa-calendar',
                'submenu': [
                    {'name': 'Listar Dias', 'url': 'lista_dias'},
                    {'name': 'Crear Dias', 'url': 'crear_dia'},
                ]
            },
            {
                'label': 'Matriculas',
                'url': 'lista_matriculas',
                'icon': 'fa fa-pencil',
                'submenu': [
                    {'name': 'Listar Matriculas', 'url': 'lista_matriculas'},
                    {'name': 'Crear Matriculas', 'url': 'crear_matricula'},
                ]
            },
            {
                'label': 'Profesor - Sede',
                'url': 'asignacion_list',
                'icon':'bi bi-person-rolodex',
                'submenu': [
                    {'name': 'Asignar Profesor Sede', 'url': 'asignacion_list'},
                    {'name': 'Crear Asignacion', 'url': 'asignacion_create'},
                ]
            },
            {
                'label': 'Calificaciones',
                'url': 'lista_calificaciones',
                'icon': 'fa fa-check-square',
                'submenu': [
                    {'name': 'Listar Calificaciones', 'url': 'lista_calificaciones'},
                    {'name': 'Asignar Calificaciones', 'url': 'seleccionar_curso_calificacion'},
                ]
            },
            {
                'label': 'Horario de Clases',
                'url': 'horario_lista',
                'icon': 'fa fa-calendar',
                'submenu': [
                    {'name': 'Listar Horarios', 'url': 'horario_lista'},
                    {'name': 'Crear Horaio', 'url': 'horario_crear'},
                ]
            },
            {
                'label': 'Pago Escolaridad',
                'url': 'lista_pagos_mensualidad',
                'icon': 'fa fa-cart-arrow-down',
                'submenu': [
                    {'name': 'Listado de Pagos', 'url': 'lista_pagos_mensualidad'},
                    {'name': 'Crear Pagos', 'url': 'crear_pago_mensualidad'},
                ]
            },
            {
                'label': 'Asitencia',
                'url': 'seleccionar_curso',
                'icon': 'fa fa-th',
                'submenu': [                    
                    {'name': 'Tomar Asistencia', 'url': 'seleccionar_curso'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    {'name': 'Listar Asistencia', 'url': 'listar_asistencia'},                     
                ]
            },
             {
                'label': 'Evaluaciones',
                'url': 'menu_evaluciones',
                'icon': 'fa fa-calendar-check',
                'submenu': [
                    {'name': 'Listar Evaluaciones', 'url': 'evaluacion_list'},
                    {'name': 'Agendar Evaluaciones', 'url': 'evaluacion_create'},
                    {'name': 'Ver Otras Agendas', 'url': 'evaluacion_otras'},             
                ]
            },         
            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa fa-print',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    
                    
                ]
            },
            {
                'label': 'Anotaciones',
                'url': 'menu_anotaciones',
                'icon': 'fa fa-comment',
                'submenu': [
                    {'name': 'Listar Anotaciones', 'url': 'lista_anotaciones'},
                    {'name': 'Crear Anotaciones', 'url': 'crear_anotacion'},                            
                ]
            }                   
        ],
        

        'PROFESOR': [
            {
                'label': 'Calificaciones',
                'url': 'lista_calificaciones',
                'icon': 'fa fa-check-square',
                'submenu': [
                    {'name': 'Listar Calificaciones', 'url': 'lista_calificaciones'},
                    {'name': 'Asignar y Editar Calificaciones', 'url': 'seleccionar_curso_calificacion'},
                ]
            },
            {
                'label': 'Asitencia',
                'url': 'seleccionar_curso',
                'icon': 'fa fa-th',
                'submenu': [
                    {'name': 'Tomar Asistencia', 'url': 'seleccionar_curso'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    {'name': 'Listar Asistencia', 'url': 'listar_asistencia'},   
                                     
                ]
            },
            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa fa-print',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                ]
            },         
            {
                'label': 'Evaluaciones',
                'url': 'menu_evaluciones',
                'icon': 'fa fa-calendar-check',
                'submenu': [
                    {'name': 'Listar Evaluaciones', 'url': 'evaluacion_list'},
                    {'name': 'Agendar Evaluaciones', 'url': 'evaluacion_create'},
                    {'name': 'Ver Otras Agendas', 'url': 'evaluacion_otras'},           
                ]
            },
            {
                'label': 'Anotaciones',
                'url': 'menu_anotaciones',
                'icon': 'fa fa-comment',
                'submenu': [
                    {'name': 'Listar Anotaciones', 'url': 'lista_anotaciones'},
                    {'name': 'Crear Anotaciones', 'url': 'crear_anotacion'},                            
                ]
            },   
            {
                'label': 'Bitacora',
                'url': 'menu_Bitacora',
                'icon': 'fa fa-address-card',
                'submenu': [   
                    {'name': 'Listar Bitacora', 'url': 'listar_bitacora'},                 
                    {'name': 'Crear Bitacora', 'url': 'crear_bitacora'},    
                     {'name': 'Informe Bitacora', 'url': 'generar_informe_bitacora'},                           
                ]
            }                    
              
                 
        ],
                
        'ALUMNO': [

            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                ]
            }         
                 
        ],
        'DIRECTOR': [

            {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa fa-print',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},                    
                ]
            },
            {
                'label': 'Evaluaciones',
                'url': 'menu_evaluciones',
                'icon': 'fa fa-calendar-check',
                'submenu': [
                    {'name': 'Listar Evaluaciones', 'url': 'evaluacion_list'},                   
                              
                ]
            },            
            {
                'label': 'Asitencia',
                'url': 'seleccionar_curso',
                'icon': 'fa fa-th',
                'submenu': [                   
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                    {'name': 'Listar Asistencia', 'url': 'listar_asistencia'},   
                                     
                ]
            },
            {
                'label': 'Anotaciones',
                'url': 'menu_anotaciones',
                'icon': 'fa fa-comment',
                'submenu': [
                    {'name': 'Listar Anotaciones', 'url': 'lista_anotaciones'},                                            
                ]
            },
            {
                'label': 'Bitacora',
                'url': 'menu_Bitacora',
                'icon': 'fa fa-address-card',
                'submenu': [   
                    {'name': 'Listar Bitacora', 'url': 'listar_bitacora'},           
                    {'name': 'Informe Bitacora', 'url': 'generar_informe_bitacora'},                 
                                          
                ]
            }      
                      
                                                 
                 
        ],
        'SECRETARIA': [
            {
                'label': 'Horario de Clases',
                'url': 'horario_lista',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Horarios', 'url': 'horario_lista'},
                    {'name': 'Crear Horaio', 'url': 'horario_crear'},
                ]
            },
            {
                'label': 'Pago Escolaridad',
                'url': 'lista_pagos_mensualidad',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Listar Pagos', 'url': 'lista_pagos_mensualidad'},
                    {'name': 'Crear Pagos', 'url': 'crear_pago_mensualidad'},
                ]
            },
                {
                'label': 'Informes',
                'url': 'menu_informes',
                'icon': 'fa-graduation-cap',
                'submenu': [
                    {'name': 'Informe Notas x Asignatura', 'url': 'seleccionar_parametros_informe'},
                    {'name': 'Informe Notas x Alumnos', 'url': 'seleccionar_parametros_informe_alumno'},
                    {'name': 'Certificado Alumno Regular', 'url': 'certificado_form'},
                    {'name': 'Informe de Asistencia', 'url': 'generar_informe'},
                ]
            }         
                 
        ],
        # ... otros roles
}