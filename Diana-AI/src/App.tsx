import { Flex } from '@chakra-ui/react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import Main from '@/components/layout/Main';

function App() {
  return (
    <Flex direction="row" w="100vw" h="100vh" overflow="hidden">
      <Sidebar />
      <Flex direction="column" flex="1" overflow="hidden">
        <Header />
        <Main />
      </Flex>
    </Flex>
  );
}

export default App;
