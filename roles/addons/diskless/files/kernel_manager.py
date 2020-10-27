# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# kernel_manager:
#    This module allow to manage kernels globaly. It
#    allow to make basic actions on kernels. 
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import basic modules
import os
from utils import *


#Class to manage kernels
class KernelManager:
    """Class to manage kernels of the diskless tool."""

    # Path where diskless kernels are
    KERNELS_PATH = '/var/www/html/preboot_execution_environment/diskless/kernels'

    @staticmethod
    def get_kernels():    
        """Get the list of kernels inside KernelManager.KERNELS_PATH.

        :return: `kernel_list` if there is at least one kernel, `None` overwise
        :rtype: list of str
        """
        # Select only files with 'vmlinuz' inside file name -> it's kernel files
        kernel_list = [kernel for kernel in os.listdir(KernelManager.KERNELS_PATH) if 'vmlinuz' in kernel]
        # if there are kernels
        if kernel_list:
            # Return kernel names list
            return kernel_list 
        else:
            return None

    @staticmethod
    def get_available_kernels():
        """Get only kernels which have an initramfs file associated in KernelManager.KERNELS_PATH.

        :return: `kernel_list` if there is at least one available kernel, `None` overwise
        :rtype: list of str
        """
        # Get all kernels
        kernel_list = KernelManager.get_kernels()
        # If there are kernels
        if kernel_list:
            # Return only kernels with initramfs-kernel
            return [kernel for kernel in kernel_list 
            if os.path.exists(KernelManager.KERNELS_PATH+'/initramfs-kernel-'+(kernel.replace('vmlinuz-','')))]
        # If there are no kernels
        else:
            return None

    @staticmethod
    def change_kernel(image, kernel):
        """Change the kernel of an image object.

        :param image: A created image object
        :type image: Image
        :param kernel: An available kernel
        :type kernel: str
        """
   
        # Use image method to set kernel 
        image.kernel = kernel
        # Register image with new kernel
        image.register_image()

    # Generate initramfs from kernel
    @staticmethod
    def generate_initramfs(kernel):
        """Generate an initramfs from a kernel. The new initramfs will be generated in KernelManager.KERNELS_PATH.

        :param kernel: A kernel in KernelManager.KERNELS_PATH
        :type kernel: str
        """
        # Create a generation path for the initramfs
        generation_path = KernelManager.KERNELS_PATH + '/initramfs-kernel-' + kernel.replace('vmlinuz-','')
                        
        printc('[INFO] Now generating initramfs... May take some time', CBLUE)
        # Generate the new initramfs file with dracut command on the kernel
        os.system('dracut --xz -v -m "network base nfs" --add "ifcfg livenet systemd systemd-initrd dracut-systemd" --add-drivers xfs --no-hostonly --nolvmconf '
                + generation_path
                + ' --force')

        # Change the permisssions on the generated file
        os.chmod(generation_path ,0o644)


    #######################
    ## CLI reserved part ##
    #######################

    @staticmethod
    def cli_select_kernel():
        """Select a kernel from an available kernels list in KernelManager.KERNELS_PATH

        :raises UserWarning: When there is no kernel to select
        :return: `kernel` if there is at least one kernel
        :rtype: str
        """
        # Get available kernels list
        kernels_list = KernelManager.get_kernels()
        # If there are available kernels
        if kernels_list:
            print('Select the kernel:')
            # return selected kernel
            return select_from_list(kernels_list)
        else:
            raise UserWarning('No available kernel.')

    # [CLI] Display a list of available kernels
    @staticmethod
    def cli_display_kernels():
        """Display all kernels inside KernelManager.KERNELS_PATH

        :raises UserWarning: When there is no kernel to display
        """
        # Get kernel list
        kernel_list = KernelManager.get_kernels()

        # If here are kernels
        if kernel_list:
            print('Available kernels:')
            print('    │')
            # For each kernel
            for kernel in kernel_list:
                # If the iniramfs file is present
                if os.path.exists(KernelManager.KERNELS_PATH+'/initramfs-kernel-'+(kernel.replace('vmlinuz-',''))):
                    initramfs_status = CGREEN +'initramfs present'+CEND
                # If the iniramfs file is not present
                else:
                    initramfs_status = CYELLOW +'missing initramfs-kernel-'+kernel.replace('vmlinuz-','') + CEND
                # If it is the last kernel of the list
                if kernel == kernel_list[-1]:
                    print("    └── "+str(kernel)+' - '+initramfs_status)
                # If it is not the last kernel of the list
                else:
                    print("    ├── "+str(kernel)+' - '+initramfs_status)

        # If the list of kernels is empty
        else:
           raise UserWarning('No kernels.')