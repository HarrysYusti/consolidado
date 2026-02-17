'use client';

import { Button, CloseButton, Dialog, Portal, Image } from '@chakra-ui/react';
import { useEffect, useState } from 'react';

interface EasterEggProps {
  show: boolean;
}
const EasterEgg = ({ show }: EasterEggProps) => {
  const [open, setOpen] = useState(show);

  useEffect(() => {
    setOpen(show);
  }, [show]);

  return (
    <Dialog.Root
      placement={'center'}
      lazyMount
      open={open}
      onOpenChange={(e) => setOpen(e.open)}
    >
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>
                Hecho con 🧡 por el equipo de tecnología
              </Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <Image
                rounded="md"
                src="/team.png"
                alt="DIANA"
                fit="cover"
                alignSelf="flex-start"
              />
            </Dialog.Body>
            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <Button variant="outline">Somos el mejor pais de Chile</Button>
              </Dialog.ActionTrigger>
            </Dialog.Footer>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

export default EasterEgg;
