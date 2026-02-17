import { lazy, useState } from 'react';
import {
  Box,
  VStack,
  IconButton,
  Text,
  useBreakpointValue,
} from '@chakra-ui/react';

import { GiHamburgerMenu } from 'react-icons/gi';

const ChatPanelControl = lazy(
  () => import('@/components/features/Chat/ChatPanelControl')
);

const Drawer = lazy(() => import('@/components/ui/Drawer'));
interface SidebarToggleProps {
  toggleExpand: () => void;
}

const SidebarToggle = ({ toggleExpand }: SidebarToggleProps) => {
  return (
    <IconButton
      px={4}
      aria-label="Abrir menú"
      variant="ghost"
      color="gray.300"
      _hover={{ bg: 'purple.950' }}
      onClick={toggleExpand}
      rounded="full"
    >
      <GiHamburgerMenu />
    </IconButton>
  );
};

const Sidebar = () => {
  const [open, setOpen] = useState(false);

  const isMobile = useBreakpointValue({ base: true, lg: false });

  return (
    <>
      <Box
        w={open && !isMobile ? '320px' : '60px'}
        bg="diana.950"
        color="gray.200"
        display="flex"
        flexDirection="column"
        justifyContent="space-between"
        py={2}
        height="100%"
        overflow="hidden"
        transition="width 0.3s ease-in-out"
      >
        {/* Parte superior */}
        <VStack align="flex-start" flex="1">
          {/* Expandir/colapsar */}

          <SidebarToggle
            toggleExpand={() => {
              setOpen((prev) => !prev);
            }}
          />

          <ChatPanelControl isExpanded={open && !isMobile} />
        </VStack>

        {/* Parte inferior: íconos secundarios */}
        <VStack align="stretch">
          <Text color={'gray.600'} textStyle="xs">
            v.{__APP_VERSION__}
          </Text>
        </VStack>
      </Box>

      {isMobile && (
        <Drawer
          open={open && isMobile}
          onClose={() => {
            setOpen(false);
          }}
        >
          <VStack align="flex-start">
            <SidebarToggle
              toggleExpand={() => {
                setOpen(false);
              }}
            />
            <ChatPanelControl
              isExpanded={true}
              callWithAction={() => setOpen(false)}
            />
          </VStack>
        </Drawer>
      )}
    </>
  );
};

export default Sidebar;
