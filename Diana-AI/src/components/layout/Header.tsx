// src/components/Banner.jsx
import { Alert, Flex, Image } from '@chakra-ui/react';
import { ColorModeButton } from '@/context/ColorMode';
import { useOnlineStatus } from '@/hooks/utils/useOnlineStatus';

function Header() {
  const isOnline = useOnlineStatus();
  return (
    <Flex
      alignItems="center"
      justifyContent="space-between"
      px={6}
      py={2}
      height={"3rem"}
      bg="diana.950"
      color="white"
      borderBottom="1px solid"
      borderColor="gray.700"
    >
      <Image
        rounded="md"
        src="/logo.png"
        alt="DIANA"
        fit="cover"
        w={16}
        alignSelf="flex-start"
      />
      {!isOnline && (
        <Alert.Root status="error" size={'sm'} width={'30rem'}>
          <Alert.Indicator />
          <Alert.Title>No estas conectado a Internet</Alert.Title>
        </Alert.Root>
      )}
      <ColorModeButton />
    </Flex>
  );
}

export default Header;
