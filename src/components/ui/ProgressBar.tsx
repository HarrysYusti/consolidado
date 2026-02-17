import { Progress } from '@chakra-ui/react/progress';

const ProgressBar = () => {
  return (
    <Progress.Root
      value={null}
      colorPalette={'purple'}
      variant="subtle"
      size={'xs'}
    >
      <Progress.Track>
        <Progress.Range />
      </Progress.Track>
    </Progress.Root>
  );
};

export default ProgressBar;
