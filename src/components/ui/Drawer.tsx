import React from 'react';
import { Drawer as D } from '@chakra-ui/react';

interface MyDrawerProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const Drawer: React.FC<MyDrawerProps> = ({ open, onClose, children }) => {
  return (
    <D.Root open={open} lazyMount onOpenChange={onClose} placement={'start'}>
      <D.Backdrop />
      <D.Trigger />
      <D.Positioner>
        <D.Content
          bg="diana.950"
          color="gray.200"
          display="flex"
          flexDirection="column"
          justifyContent="space-between"
          py={2}
          overflowY="hidden"
          height="100%"
        >
          <D.CloseTrigger />
          <D.Body p={0}>{children}</D.Body>
        </D.Content>
      </D.Positioner>
    </D.Root>
  );
};

export default Drawer;
