!###########################################################
! Creates a uindex field from a GeoModeller *.vox file     #
!                                                          #
!                                                          #
!                                                          #
!###########################################################

program units
        implicit none
        type uindex
                sequence
                integer :: u
                character (len=100) :: nam
        end type
!       uindex: An object with a name of the geological unit and
!         a unit number

        !integer, parameter :: dp = selected_real_kind (12)
        integer, parameter :: dp = selected_real_kind (8)
        real (kind=dp) :: x0, y0, z0, dx, dy, dz, x, y, z
        integer :: laenge, laenge2, old_u, i, j, mul, nxyz, add
        integer :: nx, ny, nz, n_u, u_flag, start, ix, iy, iz
        character (len=100) :: ch
        character(len=3) :: i_char
        character (len=64) input, output, bcoutp
        type(uindex) :: ui(20)
        real (kind=dp), allocatable ::  h(:,:), temp(:,:), pres(:,:)

!        Initialise variables        
        n_u=1
        mul=0
        start=0
        old_u=1
        ix=1
        iy=1
        iz=1
        add=0

!       Get the name of the vox file if given after exectuable in shell       
        call get_command_argument(1,input)

!       If vox file is not given in shell, ask for it
        if (input.eq."") then
                write (*,*) "input file:"
                read (unit=5,fmt=*) input
        end if

!       Create name of output file FORM.*        
        laenge=len_trim(input)
        output = "FORM."
        output(6:laenge+1) = input

!       Open files        
        open (unit=1, status="unknown", file=input)
        open (unit=2, status="replace", file=output)

!       Get discretisation information
        read (unit=1, fmt=*) ch, nx
        write (*,*) ch(1:2), "=", nx
        if (ch(1:2).ne."nx") then
                write(*,*) "Error: nx"
                stop
        end if
        read (unit=1, fmt=*) ch, ny
        write (*,*) ch(1:2), "=", ny
        if (ch(1:2).ne."ny") then
                write(*,*) "Error: ny"
                stop
        end if
        read (unit=1, fmt=*) ch, nz
        write (*,*) ch(1:2), "=", nz
        if (ch(1:2).ne."nz") then
                write(*,*) "Error: nz"
                stop
        end if
        read (unit=1, fmt=*) ch, x0
        write (*,*) ch(1:2), "=", x0
        if (ch(1:2).ne."x0") then
                write(*,*) "Error: x0"
                stop
        end if
        read (unit=1, fmt=*) ch, y0
        write (*,*) ch(1:2), "=", y0
        if (ch(1:2).ne."y0") then
                write(*,*) "Error: y0"
                stop
        end if
        read (unit=1, fmt=*) ch, z0
        write (*,*) ch(1:2), "=", z0
        if (ch(1:2).ne."z0") then
                write(*,*) "Error: z0"
                stop
        end if
        read (unit=1, fmt=*) ch, dx
        write (*,*) ch(1:2), "=", dx
        if (ch(1:2).ne."dx") then
                write(*,*) "Error: dx"
                stop
        end if
        read (unit=1, fmt=*) ch, dy
        write (*,*) ch(1:2), "=", dy
        if (ch(1:2).ne."dy") then
                write(*,*) "Error: dy"
                stop
        end if
        read (unit=1, fmt=*) ch, dz
        write (*,*) ch(1:2), "=", dz
        if (ch(1:2).ne."dz") then
                write(*,*) "Error: dz"
                stop
        end if

        allocate(h(nx,ny))
        allocate(temp(nx,ny))
        h=0.D0

!       Start reading units in file        
        nxyz=nx*ny*nz
        do i=1,nxyz

!               read name to ch        
                read (unit=1, fmt=*) ch
                laenge2 = len_trim(ch)
                if (ch(1:12).eq."nodata_value") then
!                       Topography: Cells above ground level are dirichlet
!                       boundaries
                        write (*,*) "Warning: Check nodata_value"
                        write (*,*) "See BC_TOP.",input(1:laenge-4), " for bc indices."
                        bcoutp = "BC_TOP."
                        bcoutp(8:laenge+3) = input
                        bcoutp(laenge+4:laenge+10)=".head"
                        open (unit=3, status="replace", file=bcoutp)
                        bcoutp(laenge+4:laenge+10)=".temp"
                        open (unit=4, status="replace", file=bcoutp)
                        bcoutp(laenge+4:laenge+10)=".pres"
                        open (unit=5, status="replace", file=bcoutp)
                        add=1
                else
                        u_flag=0                        

                        if ((ch(1:3).eq."out".and.iz.lt.nz).or.iz.eq.nz) then
!                               Hydraulic head assuming z0=0
                                write (unit=3,fmt="(i5,i5,i5,e15.4E1,i3)") ix, iy, iz, h(ix,iy), 0                          
!                               Temperature assuming average temp.
!                               gradient in air
                                write (unit=4,fmt="(i5,i5,i5,e15.4E1,i3)") ix, iy, iz, - (iz*dz + z0)*0.65/100. + 13.,0
!                               atmospheric pressure in MPa
                                write (unit=5,fmt="(i5,i5,i5,e15.4E1,i3)") ix, iy, iz, 0.101325 , 0
                        else
                                h(ix,iy) = iz*dz
                        end if

!                       Loop over all existing units that have been read till
!                       now, n_u                        

                        do j=1,n_u

!                               Check whether current unit already exists                                
                                if (ch.eq.ui(j)%nam) then
                                        if (old_u.eq.j.or.start.eq.0) then
!                                               If the same unit is encountered
!                                               more than once consecutively,
!                                               increase mul                                                        
                                                mul = mul + 1
                                                start = 2
                                        else
!                                               If the previous unit (old_u) is
!                                               different from this one, write
!                                               mul*old_u and set mul=1
                                                write (i_char, '(i3)') old_u
                                                write (unit=2,fmt="(i7,a,a)",advance="no")&
                                                    mul,"*",adjustl(i_char)
                                                 mul=1                                                 
                                                 start = 1
                                        end if
                                        u_flag = 1
                                        old_u = j                                     
                                end if
                        end do

!                       If u_flag=0, this is the first time this unit is being
!                       read. Increase mul and n_u
                        if (u_flag.eq.0) then
                                ui(n_u)%nam = ch
!                               Write name of unit and number to shell                                
                                write (*,*) ch(1:10), "=", n_u
                                if (start.eq.2) then
!                                       If mul>1 (i.e. start=2), write mul*old_u to
!                                       file and reset mul
                                        write (i_char, '(i3)') old_u
                                        write(unit=2,fmt="(i7,a,a)",advance="no")&
                                                      mul,"*",adjustl(i_char)
                                        mul=0
                                 end if
                                !write (unit=2,fmt="(i3)",advance="no") n_u
                                mul = mul + 1
                                ui(n_u)%u = n_u
                                old_u = n_u
                                n_u = n_u + 1
                                start=1
                        end if
                end if

!               Get indices ix, iy, iz
                if (start.ne.0) then
                        if (ix.lt.nx) then
                                ix = ix + 1
                        else if (iy.lt.ny) then
                                iy = iy + 1
                                ix = 1
                        else 
                                iz = iz +1
                                iy = 1
                                ix = 1
                        end if
                end if      
        end do

        deallocate(h)
        deallocate(temp)



!       Write last unit        
        write (i_char, '(i3)') old_u
        write (unit=2,fmt="(i7,a,a)",advance="no") mul+add,"*",adjustl(i_char)

!        write (unit=*,fmt="(a)") ui(1:n_u-1)%nam
!        write (*,*) ui(1:n_u-1)%u

end program units
